# Enable Virtual Env in Window

## See this link
- > https://www.sharepointdiary.com/2014/03/fix-for-powershell-script-cannot-be-loaded-because-running-scripts-is-disabled-on-this-system.html

### By default virtualenv in windows is resctricted. To enable the access, refer to following guide
- > Open PowerShell Consoles and "Run as Administrator"

### From the shell, run this command to get the current policy as "Restricted"
- > Get-ExecutionPolicy

### Then set the execution policy with following command
- > Set-ExecutionPolicy RemoteSigned

### You can also use below command to remove all resctrictions on your security policy as follow
- > Set-ExecutionPolicy Unrestricted
