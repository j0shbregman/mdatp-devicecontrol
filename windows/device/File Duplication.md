# Device control policy sample: File Duplication

Description: This is a policy.              
Device Type: Windows Removable Device

A device control policy is a combination of [policy rules](#policy-rules), [groups](#groups) and [settings](#settings).  
This sample is based on the [sample files](#files).  
To configure the sample, follow the [deployment instructions](#deployment-instructions).  

## Policy Rules


<table>
    <tr>
        <th rowspan="2" valign="top">Name</th>
        <th colspan="2" valign="top"><center>Devices</center></th>
        <th rowspan="2" valign="top">Rule Type</th>
        <th colspan="6" valign="top"><center>Access</center></th>
        <th rowspan="2" valign="top">Notification</th>
        <th rowspan="2" valign="top">Conditions</th>
    </tr>
    <tr>
        <th>Included</th>
        <th>Excluded</th>
        <th>Disk Read</th>
		<th>Disk Write</th>
		<th>Disk Execute</th>
		<th>File Read</th>
		<th>File Write</th>
		<th>File Execute</th></tr><tr>
            <td rowspan="1" valign="top"><b>Data Duplication Filesystem Demo</b></td>
            <td rowspan="1 valign="top">
                <ul><li>Group: Any Removable Storage and CD-DVD and WPD Group_1<a href="#any-removable-storage-and-cd-dvd-and-wpd-group_1" title="MatchAny {'PrimaryId': 'WpdDevices'}"> (details)</a>  
</ul>
            </td>
            <td rowspan="1" valign="top">
                <ul></ul>
            </td>
            <td>Allow</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>:white_check_mark:</td>
            <td>-</td>
            <td>Create file evidence with file (8)</td> 
            <td>
                <center>-</center></td>
        </tr></table>


## Groups


### Any Removable Storage and CD-DVD and WPD Group_1



This is a group of type *Device*. 
The match type for the group is *MatchAny*.


|  Property | Value |
|-----------|-------|
| PrimaryId | RemovableMediaDevices |
| PrimaryId | CdRomDevices |
| PrimaryId | WpdDevices |





<details>
<summary>View XML</summary>

```xml
<Group Id="{9b28fae8-72f7-4267-a1a5-685f747a7146}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData -->
	<Name>Any Removable Storage and CD-DVD and WPD Group_1</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<PrimaryId>RemovableMediaDevices</PrimaryId>
		<PrimaryId>CdRomDevices</PrimaryId>
		<PrimaryId>WpdDevices</PrimaryId>
	</DescriptorIdList>
</Group>
```
</details>


## Settings






| Setting Name |  Setting Value | Description |Documentation |
|--------------|----------------|-------------|---------------|
DefaultEnforcement | Deny | Control Device Control default enforcement. This is the enforcement applied if there are no policy rules present or at the end of the policy rules evaluation none were matched. |[documentation](https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdefaultenforcement) |
DeviceControlEnabled | True | Enables/disables device control |[documentation](https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdevicecontrolenabled) |


## Files
This policy is based on information in the following files:

- [Group Policy/Any Removable Storage and CD-DVD and WPD Group.xml](Group%20Policy/Any%20Removable%20Storage%20and%20CD-DVD%20and%20WPD%20Group.xml)
- [Group Policy/File Duplication.xml](Group%20Policy/File%20Duplication.xml)


# Deployment Instructions

Device control [policy rules](#policy-rules) and [groups](#groups) can be deployed through the following management tools:


## Windows
- [Intune UX](#intune-ux)
- [Intune Custom Settings](#intune-custom-settings)
- [Group Policy (GPO)](#group-policy-gpo)





## Intune UX

Intune UX is not supported for this policy because:
- Create file evidence with file is an unsupported notification.
- File Write (16) is an unsupported access mask

Use [Intune custom settings](#intune-custom-settings) to deploy the policy instead.


## Group Policy (GPO)
<details>
<summary>Define device control policy groups</summary>

   1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy groups.
   2. Save the XML below to a network share.
```xml
<Groups>
	<Group Id="{9b28fae8-72f7-4267-a1a5-685f747a7146}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData -->
		<Name>Any Removable Storage and CD-DVD and WPD Group_1</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<PrimaryId>RemovableMediaDevices</PrimaryId>
			<PrimaryId>CdRomDevices</PrimaryId>
			<PrimaryId>WpdDevices</PrimaryId>
		</DescriptorIdList>
	</Group>
</Groups>
```
   3. In the Define device control policy groups window, select *Enabled* and specify the network share file path containing the XML groups data.
</details>

<details>
<summary>Define device control policy rules</summary>
 
  1. Go to Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Device Control > Define device control policy rules.
  2. Save the XML below to a network share.
```xml
<PolicyRules>
	<PolicyRule Id="{7988d6d0-8854-4cad-98de-e4e22e65e058}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B7988d6d0-8854-4cad-98de-e4e22e65e058%7D/RuleData -->
		<Name>Data Duplication Filesystem Demo</Name>
		<IncludedIdList>
			<GroupId>{9b28fae8-72f7-4267-a1a5-685f747a7146}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{93cb364e-7a89-432b-8ec3-3c33096ca962}">
			<Type>Allow</Type>
			<AccessMask>16</AccessMask>
			<Options>8</Options>
		</Entry>
	</PolicyRule>
</PolicyRules>
```
  3. In the Define device control policy rules window, select *Enabled*, and enter the network share file path containing the XML rules data.
</details>

## Intune Custom Settings

<details>
<summary>Create custom intune configuration</summary>

   1. Navigate to Devices > Configuration profiles
   2. Click Create (New Policy)
   3. Select Platform "Windows 10 and Later"
   4. Select Profile "Templates"
   5. Select Template Name "Custom"
   6. Click "Create"
   7. Under Name, enter **
   8. Optionally, enter a description
   9. Click "Next" 
</details>
<details>
<summary>Add a row for Data Duplication Filesystem Demo</summary>  
   
   1. Click "Add"
   2. For Name, enter *Data Duplication Filesystem Demo*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7B7988d6d0-8854-4cad-98de-e4e22e65e058%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *windows/device/Intune OMA-URI/data_duplication_filesystem_demo{7988d6d0-8854-4cad-98de-e4e22e65e058}.xml*
         
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Any Removable Storage and CD-DVD and WPD Group_0</summary>  
   
   1. Click "Add"
   2. For Name, enter *Any Removable Storage and CD-DVD and WPD Group_0*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B9b28fae8-72f7-4267-a1a5-685f747a7146%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *windows/device/Intune OMA-URI/Any Removable Storage and CD-DVD and WPD Group.xml*
         
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for DefaultEnforcement</summary>  
   
   1. Click "Add"
   2. For Name, enter *DefaultEnforcement*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DefaultEnforcement*
   5. For Data type, select *Integer*
   
   7. For Value, enter *2*
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for DeviceControlEnabled</summary>  
   
   1. Click "Add"
   2. For Name, enter *DeviceControlEnabled*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControlEnabled*
   5. For Data type, select *Integer*
   
   7. For Value, enter *1*
   
   7. Click "Save"
</details>



