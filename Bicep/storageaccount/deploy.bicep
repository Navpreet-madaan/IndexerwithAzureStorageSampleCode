param location string = resourceGroup().location

param storageAccountName string

param DataLakeContainerNames array = [
  'raw'
  'structured'
  'curated'
]

@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param storageAccountType string

@allowed([
  'Hot'
  'Cool'
])
param accessTier string

param isHnsEnabled bool = false

param requireInfrastructureEncryption bool
param softDeleteEnabled bool

param autoDeletePolicy bool = false

param allowBlobPublicAccess bool = false

param enableDiagnostics bool = true

param DeployLogAnalytics string = 'False'
param logAnalyticsSubscriptionId string = ''
param logAnalyticsRG string = ''
param logAnalyticsName string = ''

//for private link setup
param DeployWithCustomNetworking string = 'True'
param CreatePrivateEndpoints string = 'True'
param CreatePrivateEndpointsInSameRgAsResource string = 'False'
param UseManualPrivateLinkServiceConnections string = 'False'
param vnetName string
param PrivateEndpointSubnetName string
param PrivateEndpointId string

var vnetIntegration = (DeployWithCustomNetworking == 'True' && CreatePrivateEndpoints == 'True')?true:false
var privateEndpointRg = (CreatePrivateEndpointsInSameRgAsResource == 'True')?resourceGroup().name:rgname

@description('Public Networking Access')
param DeployResourcesWithPublicAccess string = 'False'

//ip firewall rules
param AllowAccessToIpRange string = 'False'
param IpRangeCidr string = ''
var ipRangeFilter = (DeployWithCustomNetworking == 'True' && AllowAccessToIpRange == 'True')?true:false

var publicNetworkAccess = (DeployResourcesWithPublicAccess == 'True' || ipRangeFilter)?'Enabled':'Disabled'
var defaultAction = (DeployResourcesWithPublicAccess == 'True' && ipRangeFilter == false)?'Allow':'Deny'

//dns zone
@secure()
param SUBSCRIPTION_ID string
param rgname string
var blobprivateDnsZoneName = 'privatelink.blob.${environment().suffixes.storage}'
var dfsprivateDnsZoneName = 'privatelink.dfs.${environment().suffixes.storage}'
var fileprivateDnsZoneName = 'privatelink.file.${environment().suffixes.storage}'
var queueprivateDnsZoneName = 'privatelink.queue.${environment().suffixes.storage}'
var tableprivateDnsZoneName = 'privatelink.table.${environment().suffixes.storage}'

param deployblobPE bool = true
param deploydfsPE bool = false
param deployfilePE bool = true
param deployqueuePE bool = true
param deploytablePE bool = true

resource r_storageAccount 'Microsoft.Storage/storageAccounts@2021-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {
    accessTier: accessTier
    defaultToOAuthAuthentication: true
    allowBlobPublicAccess: allowBlobPublicAccess
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: publicNetworkAccess
    supportsHttpsTrafficOnly: true
    isHnsEnabled: isHnsEnabled
    encryption: {
      requireInfrastructureEncryption: requireInfrastructureEncryption
      keySource: 'Microsoft.Storage'
    }
    networkAcls: {
      defaultAction: defaultAction
      ipRules: (ipRangeFilter==false)?null:[
        {
          action: 'Allow'
          value: IpRangeCidr
        }
      ]
    }
  }
}

//define retention policy
resource r_storageAccountRetentionPolicy 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = if (softDeleteEnabled) {
  name: 'default'
  parent: r_storageAccount
  properties: {
    containerDeleteRetentionPolicy: {
      allowPermanentDelete: false
      days: 7
      enabled: true
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      days: 7
      enabled: true
    }
  }
}

resource r_autoDeletePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2022-05-01' = if (autoDeletePolicy) {
  name: 'default'
  parent: r_storageAccount
  properties: {
    policy: {
      rules: [
        {
          definition: {
            actions: {
              baseBlob: {
                delete: {
                  daysAfterCreationGreaterThan: 30
                }
              }
            }
            filters: {
              blobTypes: [
                'blockBlob'
                'appendBlob'
              ]
            }
          }
          enabled: true
          name: 'DeleteAfter30Days'
          type: 'Lifecycle'
        }
      ]
    }
  }
}

resource r_loganalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' existing = if (DeployLogAnalytics == 'True') {
  scope: resourceGroup(logAnalyticsSubscriptionId, logAnalyticsRG)
  name: logAnalyticsName
}

resource r_blob 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' existing = {
  name: 'default'
  parent: r_storageAccount
}

resource r_diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnostics && DeployLogAnalytics == 'True') {
  scope: r_blob
  name: '${r_storageAccount.name}-blob-loganalytics'
  properties: {
    workspaceId: r_loganalytics.id
    logs: [
      {
        category: 'StorageRead'
        enabled: true
      }
      {
        category: 'StorageWrite'
        enabled: true
      }
      {
        category: 'StorageDelete'
        enabled: true
      }
    ]
  }
}

resource r_storageAccountContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = [for containerName in DataLakeContainerNames: {
  name: '${r_storageAccount.name}/default/${containerName}'
}]



module m_blob_private_endpoint '../private_endpoint/deploy.bicep' = if (vnetIntegration && deployblobPE) {
  name: 'blob_private_endpoint'
  scope: resourceGroup(privateEndpointRg)
  params: {
    location:location
    vnetName: vnetName
    PrivateEndpointSubnetName: PrivateEndpointSubnetName
    UseManualPrivateLinkServiceConnections: UseManualPrivateLinkServiceConnections
    SUBSCRIPTION_ID: SUBSCRIPTION_ID
    rgname: rgname
    privateDnsZoneName:blobprivateDnsZoneName
    privateDnsZoneConfigsName:replace(blobprivateDnsZoneName,'.','-')
    resourceName: storageAccountName
    resourceID: r_storageAccount.id
    privateEndpointgroupIds: [
      'blob'
    ]
    PrivateEndpointId: PrivateEndpointId
  }
}


module m_dfs_private_endpoint '../private_endpoint/deploy.bicep' = if (vnetIntegration && deploydfsPE) {
  name: 'dfs_private_endpoint'
  scope: resourceGroup(privateEndpointRg)
  params: {
    location:location
    vnetName: vnetName
    PrivateEndpointSubnetName: PrivateEndpointSubnetName
    UseManualPrivateLinkServiceConnections: UseManualPrivateLinkServiceConnections
    SUBSCRIPTION_ID: SUBSCRIPTION_ID
    rgname: rgname
    privateDnsZoneName:dfsprivateDnsZoneName
    privateDnsZoneConfigsName:replace(dfsprivateDnsZoneName,'.','-')
    resourceName: storageAccountName
    resourceID: r_storageAccount.id
    privateEndpointgroupIds: [
      'dfs'
    ]
    PrivateEndpointId: PrivateEndpointId
  }
}

module m_file_private_endpoint '../private_endpoint/deploy.bicep' = if (vnetIntegration && deployfilePE) {
  name: 'file_private_endpoint'
  scope: resourceGroup(privateEndpointRg)
  params: {
    location:location
    vnetName: vnetName
    PrivateEndpointSubnetName: PrivateEndpointSubnetName
    UseManualPrivateLinkServiceConnections: UseManualPrivateLinkServiceConnections
    SUBSCRIPTION_ID: SUBSCRIPTION_ID
    rgname: rgname
    privateDnsZoneName:fileprivateDnsZoneName
    privateDnsZoneConfigsName:replace(fileprivateDnsZoneName,'.','-')
    resourceName: storageAccountName
    resourceID: r_storageAccount.id
    privateEndpointgroupIds: [
      'file'
    ]
    PrivateEndpointId: PrivateEndpointId
  }
}

module m_queue_private_endpoint '../private_endpoint/deploy.bicep' = if (vnetIntegration && deployqueuePE) {
  name: 'queue_private_endpoint'
  scope: resourceGroup(privateEndpointRg)
  params: {
    location:location
    vnetName: vnetName
    PrivateEndpointSubnetName: PrivateEndpointSubnetName
    UseManualPrivateLinkServiceConnections: UseManualPrivateLinkServiceConnections
    SUBSCRIPTION_ID: SUBSCRIPTION_ID
    rgname: rgname
    privateDnsZoneName:queueprivateDnsZoneName
    privateDnsZoneConfigsName:replace(queueprivateDnsZoneName,'.','-')
    resourceName: storageAccountName
    resourceID: r_storageAccount.id
    privateEndpointgroupIds: [
      'queue'
    ]
    PrivateEndpointId: PrivateEndpointId
  }
}

module m_table_private_endpoint '../private_endpoint/deploy.bicep' = if (vnetIntegration && deploytablePE) {
  name: 'table_private_endpoint'
  scope: resourceGroup(privateEndpointRg)
  params: {
    location:location
    rgname: rgname
    vnetName: vnetName
    PrivateEndpointSubnetName: PrivateEndpointSubnetName
    UseManualPrivateLinkServiceConnections: UseManualPrivateLinkServiceConnections
    SUBSCRIPTION_ID: SUBSCRIPTION_ID
    privateDnsZoneName:tableprivateDnsZoneName
    privateDnsZoneConfigsName:replace(tableprivateDnsZoneName,'.','-')
    resourceName: storageAccountName
    resourceID: r_storageAccount.id
    privateEndpointgroupIds: [
      'table'
    ]
    PrivateEndpointId: PrivateEndpointId
  }
}
