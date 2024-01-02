# Device Control Policy: Allow Authorized USB Printer

## Policy Rules
<table>
    <tr>
        <th rowspan="2" valign="top">Name</th>
        <th rowspan="2" valign="top">Devices</th>
        <th rowspan="2" valign="top">Excluding</th>
        <th rowspan="2" valign="top">Rule Type</th>
        <th colspan="7" valign="top"><center>Access</center></th>
        <th rowspan="2" valign="top">Notification</th>
        <th rowspan="2" valign="top">User SID</th>
        <th rowspan="2" valign="top">Conditions</th>
    </tr>
    <tr>
		<th>Disk Read</th>
		<th>Disk Write</th>
		<th>Disk Execute</th>
		<th>File Read</th>
		<th>File Write</th>
		<th>File Execute</th>
		<th>Print</th>
	</tr><tr>
            <td rowspan="2"><b>Allow approved USB Printer</b></td>
            <td rowspan="2 valign="top">
                <ul><li>Authorized USB Printer<a href="#authorized-usb-printer" title="MatchAny [{'VID_PID': '03F0_'}, {'VID_PID': '035E_0872'}]"> (details)</a></ul>
            </td>
            <td rowspan="2" valign="top">
                <ul></ul>
            </td>
            <td>Allow</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>:white_check_mark:</td>
            <td>None (0)</td> 
            <td>All Users</td>
            <td>MatchAny
                <ul><li> MatchAny 
                        <ul><li>Corporate Network<a href="#corporate-network" title="MatchAll [{'NameId': 'corp.microsoft.com'}, {'NetworkCategoryId': 'DomainAuthenticated'}]"> (details)</a></ul><li> MatchAny 
                        <ul><li>Corporate VPN<a href="#corporate-vpn" title="MatchAll [{'NameId': 'MSFTVPN'}, {'VPNServerAddressId': 'msftvpn.*.microsoft.com'}, {'VPNDnsSuffixId': 'corp.microsoft.com'}, {'VPNConnectionStatusId': 'Connected'}]"> (details)</a></ul>
                </ul>
            </td>
        </tr><tr>
            <td>Audit Allowed</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>:page_facing_up:</td>
            <td>Send event (2)</td>
            <td>All Users</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr></table>

## Groups


### Corporate Network

This is a group of type *Network*. 
The match type for the group is *MatchAll*.

|  Property | Value |
|-----------|-------|
| NameId | corp.microsoft.com |
| NetworkCategoryId | DomainAuthenticated |

<details>
<summary>View XML</summary>

```xml
<Group Id="{83d4b74a-af7c-4399-812c-fb9037e2c2b7}" Type="Network">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B83d4b74a-af7c-4399-812c-fb9037e2c2b7%7D/GroupData -->
	<Name>Corporate Network</Name>
	<MatchType>MatchAll</MatchType>
	<DescriptorIdList>
		<NameId>corp.microsoft.com</NameId>
		<NetworkCategoryId>DomainAuthenticated</NetworkCategoryId>
	</DescriptorIdList>
</Group>
```
</details>

### Authorized USB Printer

This is a group of type *Device*. 
The match type for the group is *MatchAny*.

|  Property | Value |
|-----------|-------|
| VID_PID | 03F0_ |
| VID_PID | 035E_0872 |

<details>
<summary>View XML</summary>

```xml
<Group Id="{05b56e90-e682-48ff-a6c0-5602c9638182}" Type="Device">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B05b56e90-e682-48ff-a6c0-5602c9638182%7D/GroupData -->
	<Name>Authorized USB Printer</Name>
	<MatchType>MatchAny</MatchType>
	<DescriptorIdList>
		<VID_PID>03F0_</VID_PID>
		<VID_PID>035E_0872</VID_PID>
	</DescriptorIdList>
</Group>
```
</details>

### Corporate VPN

This is a group of type *VPNConnection*. 
The match type for the group is *MatchAll*.

|  Property | Value |
|-----------|-------|
| NameId | MSFTVPN |
| VPNServerAddressId | msftvpn.*.microsoft.com |
| VPNDnsSuffixId | corp.microsoft.com |
| VPNConnectionStatusId | Connected |

<details>
<summary>View XML</summary>

```xml
<Group Id="{d633d17d-d1d1-4c73-aa27-c545c343b6d7}" Type="VPNConnection">
	<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bd633d17d-d1d1-4c73-aa27-c545c343b6d7%7D/GroupData -->
	<Name>Corporate VPN</Name>
	<MatchType>MatchAll</MatchType>
	<DescriptorIdList>
		<NameId>MSFTVPN</NameId>
		<VPNServerAddressId>msftvpn.*.microsoft.com</VPNServerAddressId>
		<VPNDnsSuffixId>corp.microsoft.com</VPNDnsSuffixId>
		<VPNConnectionStatusId>Connected</VPNConnectionStatusId>
	</DescriptorIdList>
</Group>
```
</details>


## Files
This policy is based on information in the following files:

- [Intune OMA-URI/Allow Authorized USB Printer.xml](Intune%20OMA-URI/Allow%20Authorized%20USB%20Printer.xml)
- [Group Policy/Printer_Groups.xml](Group%20Policy/Printer_Groups.xml)


## Intune UX

Intune UX is not supported for this policy because:
- Network groups not supported.
- VPNConnection groups not supported.
- Parameters are not supported



## GPO
### Groups
```xml
<Groups>
	<Group Id="{83d4b74a-af7c-4399-812c-fb9037e2c2b7}" Type="Network">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B83d4b74a-af7c-4399-812c-fb9037e2c2b7%7D/GroupData -->
		<Name>Corporate Network</Name>
		<MatchType>MatchAll</MatchType>
		<DescriptorIdList>
			<NameId>corp.microsoft.com</NameId>
			<NetworkCategoryId>DomainAuthenticated</NetworkCategoryId>
		</DescriptorIdList>
	</Group>
	<Group Id="{05b56e90-e682-48ff-a6c0-5602c9638182}" Type="Device">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B05b56e90-e682-48ff-a6c0-5602c9638182%7D/GroupData -->
		<Name>Authorized USB Printer</Name>
		<MatchType>MatchAny</MatchType>
		<DescriptorIdList>
			<VID_PID>03F0_</VID_PID>
			<VID_PID>035E_0872</VID_PID>
		</DescriptorIdList>
	</Group>
	<Group Id="{d633d17d-d1d1-4c73-aa27-c545c343b6d7}" Type="VPNConnection">
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bd633d17d-d1d1-4c73-aa27-c545c343b6d7%7D/GroupData -->
		<Name>Corporate VPN</Name>
		<MatchType>MatchAll</MatchType>
		<DescriptorIdList>
			<NameId>MSFTVPN</NameId>
			<VPNServerAddressId>msftvpn.*.microsoft.com</VPNServerAddressId>
			<VPNDnsSuffixId>corp.microsoft.com</VPNDnsSuffixId>
			<VPNConnectionStatusId>Connected</VPNConnectionStatusId>
		</DescriptorIdList>
	</Group>
</Groups>
```
### Rules
```xml
<PolicyRules>
	<PolicyRule Id="{f7e75634-7eec-4e67-bec5-5e7750cb9e02}" >
		<!-- ./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7Bf7e75634-7eec-4e67-bec5-5e7750cb9e02%7D/RuleData -->
		<Name>Allow approved USB Printer</Name>
		<IncludedIdList>
			<GroupId>{05b56e90-e682-48ff-a6c0-5602c9638182}</GroupId>
		</IncludedIdList>
		<ExcludedIdList>
		</ExcludedIdList>
		<Entry Id="{27c79875-25d2-4765-aec2-cb2d1000613f}">
			<Type>Allow</Type>
			<AccessMask>64</AccessMask>
			<Options>0</Options>
			<Parameters MatchType="MatchAny">
				<Network MatchType="MatchAny">
					<GroupId>{83d4b74a-af7c-4399-812c-fb9037e2c2b7}</GroupId>
				</Network>
				<VPNConnection MatchType="MatchAny">
					<GroupId>{d633d17d-d1d1-4c73-aa27-c545c343b6d7}</GroupId>
				</VPNConnection>
			</Parameters>
		</Entry>
		<Entry Id="{b280c2bf-ca5d-46a1-afc9-7e34d8098ca7}">
			<Type>AuditAllowed</Type>
			<AccessMask>64</AccessMask>
			<Options>2</Options>
		</Entry>
	</PolicyRule>
</PolicyRules>
```
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
<summary>Add a row for Allow approved USB Printer</summary>  
   
   1. Click "Add"
   2. For Name, enter *Allow approved USB Printer*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/%7Bf7e75634-7eec-4e67-bec5-5e7750cb9e02%7D/RuleData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Allow Authorized USB Printer.xml*
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Authorized USB Printer</summary>  
   
   1. Click "Add"
   2. For Name, enter *Authorized USB Printer*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B05b56e90-e682-48ff-a6c0-5602c9638182%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Authorized USB Printer.xml*
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Corporate Network</summary>  
   
   1. Click "Add"
   2. For Name, enter *Corporate Network*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7B83d4b74a-af7c-4399-812c-fb9037e2c2b7%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Corporate Network.xml*
         
   
   
   7. Click "Save"
</details>
<details>
<summary>Add a row for Corporate VPN</summary>  
   
   1. Click "Add"
   2. For Name, enter *Corporate VPN*
   3. For Description, enter **
   4. For OMA-URI, enter  *./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/%7Bd633d17d-d1d1-4c73-aa27-c545c343b6d7%7D/GroupData*
   5. For Data type, select *String (XML File)*
   
        
   6. For Custom XML, select  *.\Intune OMA-URI\Corporate VPN.xml*
         
   
   
   7. Click "Save"
</details>


## Mac

This policy is not supported on Mac because Unsupported Descriptor ID NameId
