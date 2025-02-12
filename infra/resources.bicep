@description('The location used for all deployed resources')
param location string = resourceGroup().location

@description('Tags that will be applied to all resources')
param tags object = {}


param devPythonExists bool
@secure()
param devPythonDefinition object

@description('Id of the user or app to assign application roles')
param principalId string

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location)

// Monitor application with Azure Monitor
module monitoring 'br/public:avm/ptn/azd/monitoring:0.1.0' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
    applicationInsightsDashboardName: '${abbrs.portalDashboards}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container registry
module containerRegistry 'br/public:avm/res/container-registry/registry:0.1.1' = {
  name: 'registry'
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    acrAdminUserEnabled: true
    tags: tags
    publicNetworkAccess: 'Enabled'
    roleAssignments:[
      {
        principalId: devPythonIdentity.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
      }
    ]
  }
}

// Container apps environment
module containerAppsEnvironment 'br/public:avm/res/app/managed-environment:0.4.5' = {
  name: 'container-apps-environment'
  params: {
    logAnalyticsWorkspaceResourceId: monitoring.outputs.logAnalyticsWorkspaceResourceId
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    zoneRedundant: false
  }
}

module devPythonIdentity 'br/public:avm/res/managed-identity/user-assigned-identity:0.2.1' = {
  name: 'devPythonidentity'
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}devPython-${resourceToken}'
    location: location
  }
}

module devPythonFetchLatestImage './modules/fetch-container-image.bicep' = {
  name: 'devPython-fetch-image'
  params: {
    exists: devPythonExists
    name: 'dev-python'
  }
}

var devPythonAppSettingsArray = filter(array(devPythonDefinition.settings), i => i.name != '')
var devPythonSecrets = map(filter(devPythonAppSettingsArray, i => i.?secret != null), i => {
  name: i.name
  value: i.value
  secretRef: i.?secretRef ?? take(replace(replace(toLower(i.name), '_', '-'), '.', '-'), 32)
})
var devPythonEnv = map(filter(devPythonAppSettingsArray, i => i.?secret == null), i => {
  name: i.name
  value: i.value
})

module devPython 'br/public:avm/res/app/container-app:0.8.0' = {
  name: 'devPython'
  params: {
    name: 'dev-python'
    ingressTargetPort: 80
    scaleMinReplicas: 1
    scaleMaxReplicas: 10
    secrets: {
      secureList:  union([
      ],
      map(devPythonSecrets, secret => {
        name: secret.secretRef
        value: secret.value
      }))
    }
    containers: [
      {
        image: devPythonFetchLatestImage.outputs.?containers[?0].?image ?? 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        name: 'main'
        resources: {
          cpu: json('0.5')
          memory: '1.0Gi'
        }
        env: union([
          {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            value: monitoring.outputs.applicationInsightsConnectionString
          }
          {
            name: 'AZURE_CLIENT_ID'
            value: devPythonIdentity.outputs.clientId
          }
          {
            name: 'PORT'
            value: '80'
          }
        ],
        devPythonEnv,
        map(devPythonSecrets, secret => {
            name: secret.name
            secretRef: secret.secretRef
        }))
      }
    ]
    managedIdentities:{
      systemAssigned: false
      userAssignedResourceIds: [devPythonIdentity.outputs.resourceId]
    }
    registries:[
      {
        server: containerRegistry.outputs.loginServer
        identity: devPythonIdentity.outputs.resourceId
      }
    ]
    environmentResourceId: containerAppsEnvironment.outputs.resourceId
    location: location
    tags: union(tags, { 'azd-service-name': 'dev-python' })
  }
}



// Create a keyvault to store secrets
module keyVault 'br/public:avm/res/key-vault/vault:0.6.1' = {
  name: 'keyvault'
  params: {
    name: '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    enableRbacAuthorization: false
    accessPolicies: [
      {
        objectId: principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
      {
        objectId: devPythonIdentity.outputs.principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
    ]
    secrets: [
    ]
  }
}


// Create a storage account
module storageAccount 'br/public:avm/res/storage/storage-account:0.6.0' = {
  name: 'storageAccount'
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
    skuName: 'Standard_LRS'
    kind: 'StorageV2'
    //allow access from all public networks
    publicNetworkAccess: 'Enabled'

  }

}

resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' =  {
  name: '${abbrs.storageStorageAccounts}${resourceToken}/default/uploads'
  properties: {
    publicAccess: 'None'
  }
}
  
resource storageLifecyclePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2021-04-01' = {
  name: '${abbrs.storageStorageAccounts}${resourceToken}/default'
  properties: {
    policy: {
      rules: [
        {
          enabled: true
          name: 'deleteAfterOneDay'
          type: 'Lifecycle'
          definition: {
            actions: {
              baseBlob: {
                delete: {
                  daysAfterModificationGreaterThan: 1
                }
              }
            }
            filters: {
              blobTypes: [ 'blockBlob' ]
              prefixMatch: [ 'uploads/' ]
            }
          }
        }
      ]
    }
  }
}



output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_RESOURCE_DEV_PYTHON_ID string = devPython.outputs.resourceId
output STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name


