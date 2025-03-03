//Assigns the Devcenter identity the permission to read secrets
param keyVaultName string
param sharedrgName string
param sharedsubscriptionid string
param managedid string = 'Computegalleryid'
//param userAssignedIdentityId string 

resource kv 'Microsoft.KeyVault/vaults@2021-11-01-preview' existing = {
  name: keyVaultName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  scope: resourceGroup(sharedsubscriptionid,sharedrgName)
  name: managedid
}
//output userAssignedIdentityId string = managedIdentity.properties.principalId

var keyVaultSecretsUserRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')

resource rbacSecretUserSp 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: kv
  name: guid(kv.id, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalType: 'ServicePrincipal'
    principalId: managedIdentity.properties.principalId
  }
}




