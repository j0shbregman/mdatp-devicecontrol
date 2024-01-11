#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse
import os, sys
import pandas as pd
import jinja2
import pathlib
import urllib.parse
import copy
import json

import convert_dc_policy as mac 


def xml_safe_text(text):

    try:
        
        ET.fromstring("<test>"+text+"</test>")
        return text
    except Exception as e:
        out = str(text).replace("&","&amp;")
        out = str(out).replace("<","&lt;")
        out = str(out).replace(">","&gt;")
        out = str(out).replace("'","&apos;")
        out = str(out).replace("\"","&quot;")
        return out

def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

# from  https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def clean_up_name(name, new_space = "-"):

    clean_name = name
    clean_name = str(clean_name).lstrip()
    clean_name = str(clean_name).rstrip()
    clean_name = str(clean_name).lower()
    clean_name = str(clean_name).replace(" ",new_space)
    clean_name = str(clean_name).replace("(","")
    clean_name = str(clean_name).replace(")","")
    clean_name = str(clean_name).replace(",","")

    return clean_name


class Setting: 

    
    OMA_URI_Integer_DataType = "Integer"
    OMA_URI_XML_DataType = "String (XML File)"
    OMA_URI_String_DataType = "String"

    DeviceControlEnabled = "DeviceControlEnabled"
    DefaultEnforcement = "DefaultEnforcement"
    DataDuplicationDirectory = "DataDuplicationDirectory"
    SecuredDevicesConfiguration = "SecuredDevicesConfiguration"
    DataDuplicationMaximumQuota = "DataDuplicationMaximumQuota"
    DataDuplicationRemoteLocation = "DataDuplicationRemoteLocation"

    data = {
        DeviceControlEnabled:{
            "description":"Enables/disables device control",
            "oma-uri": {
                "name": "Device Control Enabled",
                "oma-uri": "./Vendor/MSFT/Defender/Configuration/DeviceControlEnabled",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdevicecontrolenabled",
                "type": OMA_URI_Integer_DataType,
                "value_map": {
                    True: 1,
                    False: 0
                }
            },
            "gpo":{

            }
        },
        DefaultEnforcement:{
            "oma-uri": {
                "name": "Default Enforcement",
                "oma-uri":"./Vendor/MSFT/Defender/Configuration/DefaultEnforcement",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdefaultenforcement",
                "type": OMA_URI_Integer_DataType,
                "value_map":{
                    "Allow": 1,
                    "Deny": 2
                }
            }
        },
        DataDuplicationDirectory:{
            "oma-uri": {
                "name": "File Evidence Directory",
                "oma-uri":"./Device/Vendor/MSFT/Defender/Configuration/DataDuplicationDirectory",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdataduplicationdirectory",
                "type": OMA_URI_String_DataType
            }
        },
        SecuredDevicesConfiguration: {
            "oma-uri": {
                "name": "Secured Devices",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationsecureddevicesconfiguration",
                "oma-uri": "./Vendor/MSFT/Defender/Configuration/SecuredDevicesConfiguration",
                "type": OMA_URI_String_DataType
            }
        },
        DataDuplicationMaximumQuota:{
            "oma-uri":{
                "name": "File Evidence Quota",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdataduplicationmaximumquota",
                "oma-uri": "./Device/Vendor/MSFT/Defender/Configuration/DataDuplicationMaximumQuota",
                "type": OMA_URI_Integer_DataType
            }
        },
        DataDuplicationRemoteLocation:{
            "oma-uri":{
                "name": "File Evidence Remote Location",
                "oma-uri": "./Device/Vendor/MSFT/Defender/Configuration/DataDuplicationRemoteLocation",
                "documentation": "https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp#configurationdataduplicationremotelocation",
                "type": OMA_URI_String_DataType
            }
        }
    }
    
    def __init__(self,name,value):
        self.name = name
        self.value = value
        

        if name not in Setting.data.keys():
            raise Exception("Unknown Setting "+name)
        

    def get_data_type(self, format = "oma-uri"):
         return Setting.data[self.name][format]["type"]
    
    def get_documentation(self, format="oma-uri"):
        return Setting.data[self.name][format]["documentation"]

    def get_oma_uri(self):

        return Setting.data[self.name]["oma-uri"]["oma-uri"]

    def get_value(self,format = "oma-uri"):

        if format == "oma-uri":
            oma_uri = Setting.data[self.name]["oma-uri"]
            if oma_uri["type"] == Setting.OMA_URI_String_DataType:
                return self.value
            elif oma_uri["type"] == Setting.OMA_URI_Integer_DataType:
                if "value_map" in oma_uri.keys():
                    return int(oma_uri["value_map"][self.value])
                else:
                    return self.value
            else:
                return self.value
            
        else:
            return self.value




class Settings:

    def __init__(self, setting_dict):
        self.settings = []
        for name in setting_dict:
            value = setting_dict[name]
            self.settings.append(Setting(name,value))

    def getIntuneCustomValues(self):
        custom_rows = {}

        for setting in self.settings:
            row = IntuneCustomRow(setting)
            custom_rows[row.OMA_URI] = row

        return custom_rows
    
    def __iter__(self):
        return self.settings.__iter__()

    def __next__(self): 
        return self.settings.__next__()

class IntuneCustomRow:


    def __init__(self,object):
        self.name = ""
        self.description = ""
        self.OMA_URI = ""
        self.data_type = Setting.OMA_URI_XML_DataType
        self.value = ""
        self.object = object

        match object.__class__.__name__:

            case "Group":
                self.name = object.name
                self.OMA_URI = object.get_oma_uri()
                self.value = object.path
            case "PolicyRule":
                self.name = object.name
                self.OMA_URI = object.get_oma_uri()
                self.value = object.path
            case "Setting":
                self.name = object.name
                self.OMA_URI = object.get_oma_uri()
                self.value = object.get_value("oma-uri")
                self.data_type = object.get_data_type("oma-uri")
            case other:
                print ("Unknown object class "+str(object.__class__.__name__))
            
class Property:

    def __init__(self, property_name, property_value):
        self.name = property_name
        self.value = property_value

class Clause:


    def __init__(self,clause):
        self._properties = []
        self.sub_clauses = []
        self.sub_clause_type = None

        property = None
        value = None
        if "$type" in clause:
            property = clause.get("$type")
            if property == "and" or property == "or":
                self.sub_clause_type = property
                if "clauses" in clause:
                    self.has_sub_clauses = True
                    clauses = clause.get("clauses")
                    for subclause in clauses:
                        sc = Clause(subclause)
                        self.sub_clauses.append(sc)
                        
                        

            if "value" in clause:
                value = clause.get("value")

            if property is not None and value is not None:
                self._properties.append(Property(property, value))
            elif self.sub_clause_type is None:
                print("Unknown Clause")
                return


class Group:

    supported_match_types = [
        "MatchAny",
        "MatchAll"
    ]

    def __init__(self,root,format,path):

        self.format = format
        self.path = path
        self._properties = []
        self.clauses = []
        self.root = root
        self.conditions = {}

        if format == "gpo" or format =="oma-uri":

            self.id = root.attrib["Id"]
            if "Type" in root.attrib.keys():
                self.type = root.attrib["Type"]
            else:
                self.type = "Device"

            name_node = root.find(".//Name")
            if name_node is None:
                self.name = "?"
            else:
                self.name = name_node.text

            match_node = root.find(".//MatchType")
            if match_node is None:
                if "MatchType" in root.attrib.keys():
                    self.match_type = root.attrib["MatchType"]
                else:
                    self.match_type = "?"
            else:
                self.match_type = match_node.text
            
            descriptors = root.findall("./DescriptorIdList//")
            for descriptor in descriptors:
                self._properties.append(Property(descriptor.tag, descriptor.text))
                self.conditions[descriptor.tag] = descriptor.text

        elif format == "mac":
            if "id" in root.keys():
                self.id = root["id"]

            if "name" in root.keys():
                self.name = root["name"]

            if "$type" in root.keys():
                self.type = root["$type"]

            if "query" in root.keys():
                query = root["query"]

                if "$type" in query.keys():
                    self.match_type = query["$type"]

                if "clauses" in query.keys():
                    clauses = query["clauses"]
                    for clause in clauses:
                        self.clauses.append(Clause(clause))

                self.conditions = clauses

    def get_oma_uri(self):
        return "./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyGroups/"+urllib.parse.quote_plus(self.id)+"/GroupData"
    
    def get_section_title(self):

        return clean_up_name(self.name)
    
    def get_conditions(self):
        return self.conditions

    def toXML(self,indent = "\t"):

        out = indent + "<Group Id=\""+self.id+"\" Type=\""+self.type+"\">\n"
        out +=indent + "\t<!-- "+self.get_oma_uri()+" -->\n"
        out +=indent + "\t<Name>"+xml_safe_text(self.name)+"</Name>\n"
        out +=indent + "\t<MatchType>"+self.match_type+"</MatchType>\n"
        out +=indent + "\t<DescriptorIdList>\n"
        
        for property in self._properties:
            tag = property.name
            text = property.value

            out += indent +"\t\t<"+tag+">"+xml_safe_text(text)+"</"+tag+">\n"

        out += indent +"\t</DescriptorIdList>\n"
        out += indent +"</Group>"

        return out
    
    def toJSON(self):
        return json.dumps(self.root)
    
    def __str__(self):
        if self.format != "mac":
            return self.toXML()
        else:
            return self.toJSON()
    
    def __eq__(self,other):
        if self.match_type == other.match_type and len(self._properties) == len(other._properties):
            for property in self._properties:
                if property in other._properties:
                    continue
                else:
                    return False
            return True
        return False
    
    def __hash__(self):
        hashList = []
        for property in self._properties:
            key = property.name
            value = property.value
            hashList.append(key+"="+value)

        hashList.append ("type="+self.match_type)

        hashList.sort()
        return hash(str(hashList))

class PolicyRule:

    def __init__(self,root, rule_index = 1):
        self.id = root.attrib["Id"]
        name_node = root.find(".//Name")
        if name_node is None:
            self.name = "?"
        else:
            self.name = name_node.text

        self.included_groups = []
        self.excluded_groups = []
        self.entries = []
        self.has_printing = False

        included_groups_node = root.find(".//IncludedIdList")
        if not included_groups_node is None:
            groups = included_groups_node.findall(".//GroupId")
            for group in groups:
                self.included_groups.append(group.text)

        excluded_groups_node = root.find(".//ExcludedIdList")
        if not excluded_groups_node is None:
            groups = excluded_groups_node.findall(".//GroupId")
            for group in groups:
                self.excluded_groups.append(group.text)

        for entry in root.findall(".//Entry"):
            newEntry = Entry(entry)
            if newEntry.has_printing:
                self.has_printing = True

            self.entries.append(Entry(entry))        

                    
        self.format = ""
        self.path = ""        
        self.rule_index = rule_index
        return

    def get_oma_uri(self):
        return "./Vendor/MSFT/Defender/Configuration/DeviceControl/PolicyRules/"+urllib.parse.quote_plus(self.id)+"/RuleData"
    
    def toXML(self,indent = "\t"):

        out = indent + "<PolicyRule Id=\""+self.id+"\" >\n"
        out +=indent + "\t<!-- "+self.get_oma_uri()+" -->\n"
        out +=indent + "\t<Name>"+xml_safe_text(self.name)+"</Name>\n"
        
        out +=indent + "\t<IncludedIdList>\n"
        for group in self.included_groups:
            out += indent +"\t\t<GroupId>"+group+"</GroupId>\n"
        out +=indent + "\t</IncludedIdList>\n"

        out += indent +"\t<ExcludedIdList>\n"
        for group in self.excluded_groups:
            out += indent +"\t\t<GroupId>"+group+"</GroupId>\n"
        out += indent +"\t</ExcludedIdList>\n"

        for entry in self.entries:

            out += entry.toXML(indent+"\t")


        out += indent +"</PolicyRule>"

        return out
    
    def __eq__(self,other):
        self_xml = self.toXML()
        other_xml = other.toXML()
        return self_xml == other_xml
    
    def __hash__(self):
        return hash(self.toXML())
class Entry:



    access_masks = {
        0x01: "Disk Read",
        0x02: "Disk Write",
        0x04: "Disk Execute",
        0x08: "File Read",
        0x10: "File Write",
        0x20: "File Execute",
        0x40: "Print"
    }

    access_mask_text_labels = {
        0x01: "Read",
        0x02: "Write",
        0x04: "Execute",
        0x40: "Print"
    }

    allow_notification_masks = {
        0x04: "Disable",
        0x08: "Create File Evidence"
    }

    deny_notification_masks = {
        0x04: "Disable"
    }

    audit_allowed_notification_masks = {
        0x01: "None",
        0x02: "Send event"
    }

    audit_denied_notification_masks = {
        0x01: "Show notification",
        0x02: "Send event"
    }

    notification_masks = {
        "Allow": allow_notification_masks,
        "AuditAllowed": audit_allowed_notification_masks,
        "Deny": deny_notification_masks,
        "AuditDenied": audit_denied_notification_masks
    }

    type_label = {
        "Allow": "Allow",
        "AuditAllowed": "Audit Allowed",
        "Deny": "Deny",
        "AuditDenied": "Audit Denied"
    }

    true_icons = {
        "Allow":":white_check_mark:",
        "AuditAllowed":":page_facing_up:",
        "Deny":":x:",
        "AuditDenied":":page_facing_up:"
    }

    def __init__(self,entry):
        self.id = entry.attrib["Id"]
        self.type = entry.find("./Type").text
        self.type_text = Entry.type_label[self.type]
        self.options = entry.find("./Options").text
        self.access_mask = entry.find("./AccessMask").text
        self.has_printing = False

        self.permissions = {
            1: False,
            2: False,
            4: False,
            8: False,
            16: False,
            32: False,
            64: False
        }

        self.permission_icons = {
            1: "-",
            2: "-",
            4: "-",
            8: "-",
            16: "-",
            32: "-",
            64: "-"
        }



        self.notifications = []
        self.access_mask_text = ""
        self.options_text = ""

        for mask in Entry.access_masks.keys():
            if int(self.access_mask) & mask:
                self.permissions[mask] = True
                if mask in Entry.access_mask_text_labels:
                    self.access_mask_text = self.access_mask_text+", "+Entry.access_mask_text_labels[mask]
                self.permission_icons[mask] = Entry.true_icons[self.type]
                if mask == 64:
                    self.has_printing = True

        #replaces last , with and
        self.access_mask_text = self.access_mask_text[2:]
        self.access_mask_text = rreplace(self.access_mask_text,","," and",1)
        

        notification_masks = Entry.notification_masks[self.type]
        for mask in notification_masks:
            if int(self.options) & mask:
                self.notifications.append(notification_masks[mask])
        
        if len(self.notifications) == 0:
            self.notifications.append("None")
            self.options_text = "None"
        elif len(self.notifications) == 1:
            self.options_text = self.notifications[0]
        else:
            self.options_text = self.notifications[0]+" and "+self.notifications[1]

        sid = entry.find("./Sid")
        if sid is not None:
            self.sid = sid.text
        else:
            self.sid = "All Users"

        parameters = entry.find("./Parameters")
        if parameters is not None:
            self.parameters = Parameters(parameters)
        else:
            self.parameters = None
        return
    
    def get_group_ids(self):
        if self.parameters is not None:
            return self.parameters.get_group_ids()
        else:
            return []
    
    def toXML(self,indent):

        out = indent + "<Entry Id=\""+self.id+"\">\n"
        out += indent +"\t<Type>"+self.type+"</Type>\n"
        out += indent +"\t<AccessMask>"+self.access_mask+"</AccessMask>\n"
        out += indent +"\t<Options>"+self.options+"</Options>\n"

        if self.sid != "All Users":
            out += indent +"\t<Sid>"+self.sid+"</Sid>\n"

        if self.parameters is not None:
            out += self.parameters.toXML(indent+"\t")
            

        out += indent +"</Entry>\n"

        return out
    
    def validateSupport(self,feature_data,support):

        unsupported_access_masks = feature_data["unsupported_access_masks"]

        for mask in self.permissions.keys():
            enabled = self.permissions[mask]
            if enabled and unsupported_access_masks[mask]:
                support.issues.append(Entry.access_masks[mask]+" ("+str(mask)+") is an unsupported access mask")

        if self.type not in feature_data["supported_types"]:
            support.issues.append("Unsupported type of entry "+self.type)
        else:
            unsupported_notifications = feature_data["supported_types"][self.type]["unsupported_notifications"]
            notification_masks_for_type = Entry.notification_masks[self.type]
            for mask in notification_masks_for_type:
                if int(self.options) & mask:
                    if unsupported_notifications[mask]:
                        support.issues.append(notification_masks_for_type[mask]+" ("+str(mask)+") is an unsupported notification.")

        if self.parameters is not None:
            if "parameters" not in feature_data.keys():
                support.issues.append("Parameters are not supported")

        
class Parameters:

    def __init__(self,parameters):
        self.match_type = parameters.attrib['MatchType']
        self.conditions = []
        for condition in parameters.findall("./"):
            match condition.tag:
                case "Network":
                    self.conditions.append(Condition(condition))
                case "VPNConnection":
                    self.conditions.append(Condition(condition))
                case "File":
                    self.conditions.append(Condition(condition))
                case "Parameters":
                    self.conditions.append(Parameters(condition))
                case other:
                    raise Exception('Unknown condition '+condition.tag)

    def get_group_ids(self):
        groups = []
        for condition in self.conditions:
            group_ids = condition.get_group_ids()
            for group_id in group_ids:
                groups.append(group_id)

        return groups

    def toXML(self,indent):

        out = indent + "<Parameters MatchType=\""+self.match_type+"\">\n"

        for condition in self.conditions:
            out += condition.toXML(indent+"\t")

        out += indent + "</Parameters>\n"

        return out

class Condition:
    def __init__(self,condition):
        self.match_type = condition.attrib['MatchType']
        self.groups = []
        self.tag = condition.tag
        self.condition_type = condition.tag
        for group in condition.findall(".//GroupId"):
            self.groups.append(group.text)

    def get_group_ids(self):
        return self.groups
    
    def toXML(self,indent):
        out = indent + "<"+self.tag+" MatchType=\""+self.match_type+"\">\n"

        for group in self.groups:
            out += indent +"\t<GroupId>"+group+"</GroupId>\n"

        out += indent + "</"+self.tag+">\n"

        return out

class Support:

    def __init__(self):
        self.issues = []

    def isValid(self):
        return len(self.issues) == 0
    
    def __add__(self,other):
        result = copy.copy(self)
        result.issues = list(set(other.issues+self.issues))

        return result
    
class Feature:

    def get_unsupported_dictionary(supported_values):
        unsupported_access_masks = {
            1: True,
            2: True,
            4: True,
            8: True,
            16: True,
            32: True,
            64: True
        } 

        for value in supported_values:
            unsupported_access_masks[value] = False

        return unsupported_access_masks

    def __init__(self, feature_data):
        self.feature_data = feature_data
        self.support_data = {}
        entry_data = self.feature_data["entry"]
        entry_data["unsupported_access_masks"] = Feature.get_unsupported_dictionary(entry_data["access_masks"])
        for type in entry_data["supported_types"]:
            notifications = entry_data["supported_types"][type]["notifications"]
            entry_data["supported_types"][type]["unsupported_notifications"] = Feature.get_unsupported_dictionary(notifications)



    def get_support_for(self,object):

        if object.id in self.support_data.keys():
            return self.support_data[object.id]
        
        support = Support()
        self.support_data[object.id] = support

        match object.__class__.__name__:
            case "Group":
                group_support = self.feature_data["group"]
                supported_group_types = group_support["supported_types"]
                if object.type not in supported_group_types:
                    support.issues.append(object.type+" groups not supported.")
                else:
                    supported_properties = supported_group_types[object.type]["properties"]
                    for property in object._properties:
                        propertyId = property.name
                        value = property.value
                        if propertyId not in supported_properties:
                            support.issues.append(propertyId+" not supported for "+object.type+" group.")
                        else: 
                            if "values" in supported_properties[propertyId].keys() and value not in supported_properties[propertyId]["values"]:
                                support.issues.append(value+" not supported for "+propertyId+" of "+object.type+" group.")

                supported_match_types = group_support["match_types"]
                if object.match_type not in supported_match_types:
                    support.issues.append(object.match_type+" not supported.")

            case "PolicyRule":
                
                entry_support = self.feature_data["entry"]
                for entry in object.entries:
                    entry.validateSupport(entry_support,support)


        return support


class Inventory:

    
    def __init__(self,source_path,generate_oma_uri=False,dest="."):
        self.paths = source_path
        self.generate_oma_uri = generate_oma_uri
        self.dest_dir = dest

        group_columns = {
            "type":[],
            "path":[],
            "format":[],
            "name":[],
            "id":[],
            "match_type":[],
            "object":[]
        }

        rule_columns = {
            "path":[],
            "format":[],
            "name":[],
            "id":[],
            "included_groups":[],
            "excluded_groups":[],
            "object":[],
            "rule_index":[]
        }

        self.groups = pd.DataFrame(group_columns)
        self.policy_rules = pd.DataFrame(rule_columns)

        self.intune_ux = Feature(
        {
            "group": {
                "supported_types": {
                    "Device":{
                        "properties":{
                            "BusId":{},
                            "DeviceId":{},
                            "FriendlyNameId":{},
                            "HardwareId":{},
                            "InstancePathId":{},
                            "VID_PID":{},
                            "VID":{},
                            "PID":{},
                            "PrimaryId":{
                                "values":["RemovableMediaDevices", 
                                          "CdRomDevices",
                                           "WpdDevices",
                                           "PrinterDevices"]
                            },
                            "SerialNumberId":{},
                            "PrinterConnectionId":{
                                "values":[
                                    "USB",
                                    "Corporate",
                                    "Network",
                                    "Universal",
                                    "File",
                                    "Custom",
                                    "Local"
                                ]
                            }
                        }
                    }
                },
                "match_types": ["MatchAll","MatchAny"]
            },
            "entry":{
                "access_masks":[1,2,4,64],
                "supported_types":{
                    "Allow":{
                        "notifications":[0,4]
                    },
                    "AuditAllowed":{
                        "notifications":[0,1,2]
                    },
                    "Deny":{
                        "notifications":[0,2]
                    },
                    "AuditDenied":{
                        "notifications":[0,1,2]
                    }

                }
            }
        })
    
 

        self.load_inventory()

        

    def load_inventory(self):
        for path in self.paths:
            for dir in os.walk(top=path):
                files = dir[2]
                for file in files:
                    if str(file).endswith(".xml"):
                        xml_path = dir[0]+os.sep+file
                        self.load_xml_file(xml_path)
                    if str(file).endswith(".json"):
                        json_path = dir[0]+os.sep+file
                        self.load_json_file(json_path)

    
    
    def load_json_file(self,json_path):
        try:
            with open(json_path) as file:
                json_object = json.load(file)

                if "groups" in json_object.keys():
                    group_index = 1
                    for group in json_object["groups"]:
                        self.addGroup(Group(group,"mac",json_path),group_index)
                        group_index=group_index+1

            return
        except Exception as e:
            print(full_stack())
            print ("Error in "+json_path+": "+str(e))
            return
    
    def load_xml_file(self,xml_path):
        try:
            with open(xml_path) as file:
                root = ET.fromstring(file.read())
                match root.tag:
                    case "Group":
                        self.addGroup(Group(root,"oma-uri",xml_path))
                    case "Groups":
                        group_index = 1
                        for group in root.findall(".//Group"):
                            self.addGroup(Group(group,"gpo",xml_path), group_index)
                            group_index=group_index+1
                    case "PolicyGroups":
                        #This is what Intune UX looks like on disk
                        group_index = 1
                        for group in root.findall(".//Group"):
                            self.addGroup(Group(group,"gpo",xml_path), group_index)
                            group_index=group_index+1
                    case "PolicyRule":
                        self.addPolicyRule(PolicyRule(root),xml_path,"oma-uri")
                    case "PolicyRules":
                        rule_index = 1
                        for policyRule in root.findall(".//PolicyRule"):
                            self.addPolicyRule(PolicyRule(policyRule,rule_index),xml_path,"gpo",rule_index)
                            rule_index= rule_index + 1

                return root

        except Exception as e:
            print(full_stack())
            print ("Error in "+xml_path+": "+str(e))
            return

    def addGroup(self,group, group_index=0):

        
        path = group.path
        format = group.format

        if group.name == "?":
            paths = str(path).split(os.sep)
            last_path = paths[-1]
            fileWithoutExtension = last_path.split(".")[0]
            group.name = fileWithoutExtension+"_"+str(int(group_index))


        #Could check for Intune UX support
        new_row = pd.DataFrame([{
            "type":group.type,
            "path":path,
            "format":format,
            "name":group.name,
            "id":group.id,
            "match_type":group.match_type,
            "object": group
        }])

        self.groups = pd.concat([self.groups,new_row],ignore_index=True)

    def addPolicyRule(self,rule,path,format="gpo",rule_index=1):

        rule.format = format
        rule.path = path
        rule.rule_index = rule_index

        
        new_row = pd.DataFrame([{
            "path":path,
            "format":format,
            "name":rule.name,
            "id":rule.id,
            "included_groups":rule.included_groups,
            "excluded_groups":rule.excluded_groups,
            "object": rule,
            "rule_index": rule_index
        }])

        self.policy_rules = pd.concat([self.policy_rules,new_row],ignore_index=True)

        return
    
    def get_groups_for_rule(self,rule):
        groups_for_rule = {
            "gpo":[],
            "oma-uri":[]
        }
        for included_group in rule.included_groups:
            g = self.get_group_by_id(included_group)
            if g is not None:
                groups_for_rule["gpo"] += g["gpo"] 
                groups_for_rule["oma-uri"] += g["oma-uri"]

        for excluded_group in rule.excluded_groups:
            g = self.get_group_by_id(excluded_group)
            if g is not None:
                groups_for_rule["gpo"] += g["gpo"]
                groups_for_rule["oma-uri"] += g["oma-uri"]

        for entry in rule.entries:
            groups = entry.get_group_ids()
            for entry_group in groups:
                g = self.get_group_by_id(entry_group)
                if g is not None:
                    groups_for_rule["gpo"] += g["gpo"]
                    groups_for_rule["oma-uri"] += g["oma-uri"]
        
        return groups_for_rule


    def get_group_by_id(self,group_id):
        group_frame = self.groups.query("id == '"+group_id+"'")
        if group_frame.size == 0:
            print ("No group found for "+group_id)
            return None
        else:
            groups = {
                "gpo":[],
                "oma-uri":[]
            }
            for i in range(0,group_frame.index.size):
                group = group_frame.iloc[i]["object"]
                format = group_frame.iloc[i]["format"]
                path = group_frame.iloc[i]["path"]
                if group in groups[format]:
                    continue
                elif len(groups[format]) == 0:
                    groups[format].append(group)
                else:
                    print("Conflicting groups for "+group_id+" at "+path+"\n"+str(group) +"\n!=\n" +str(groups[format][0]))

            if len(groups["oma-uri"]) == 0:
                oma_uri_group = self.missing_oma_uri(groups["gpo"][0])
                if oma_uri_group is not None:
                    groups["oma-uri"].append(oma_uri_group)

            return groups
    
    def get_path_for_group(self,group_id):
        group_frame = self.groups.query("id == '"+group_id+"'")
        return group_frame.iloc[0]["path"]
    

    def query_policy_rules(self,query):
        rules = {
            "gpo":{},
            "oma-uri":{},
            "all":[]
        }

        
        rule_frame = self.policy_rules.query(query, engine='python')
        rule_frame = rule_frame.sort_values("rule_index", ascending=True)
        for i in range(0,rule_frame.index.size):
            rule = rule_frame.iloc[i]["object"]
            format = rule_frame.iloc[i]["format"]
            rule_index = rule_frame.iloc[i]["rule_index"]
            rule_id = rule.id

            if format == "oma-uri":
                rule_id = rule.get_oma_uri()

            rules_for_format = rules[format]
            if rule_id in rules_for_format:
                existing_rule = rules_for_format[rule_id]
                if existing_rule != rule:
                    print ("Conflicting rules for id "+rule.id+"\n"+str(rule)+"\n!=\n"+str(existing_rule))
            elif format == "oma-uri":
                rules[format][rule_id] = IntuneCustomRow(rule)
            else:
                rules[format][rule_id] = rule 

            rules["all"].append(rule)

        rules["all"] = list(set(rules["all"]))
        rules["all"].sort(key= lambda x: x.rule_index)

        #check for missing oma-uri rules
        for rule in rules["all"]:
            if not rule.get_oma_uri() in rules["oma-uri"]:
                oma_uri_rule = self.missing_oma_uri(rules["gpo"][rule.id])
                if oma_uri_rule is not None:
                    rules["oma-uri"][rule.get_oma_uri()] = IntuneCustomRow(oma_uri_rule)

        return rules
    

    def missing_oma_uri(self,object):
        print("Missing oma-uri for id "+object.id)
        oma_uri_object = copy.copy(object)
        oma_uri_object.format = "oma-uri"


        if self.generate_oma_uri:
            current_object_dir = os.path.dirname(object.path)
            path = current_object_dir + os.sep + clean_up_name(oma_uri_object.name,"_")+oma_uri_object.id + ".xml"
            oma_uri_object.path = path
            with open(path,"w") as generated_file:
                generated_file.write(oma_uri_object.toXML(""))
                generated_file.close()

        else:
            oma_uri_object.path = None

        return oma_uri_object
    
    def process_query(self,query):

        if query is None:
            query="path.str.contains('(.*)')"

        filtered_rules = self.query_policy_rules(query)

        result = {}

        rules = {}
        groups = {}
        paths = []
        intune_ux_support = Support()
        groupsXML = "<Groups>"
        rulesXML  = "<PolicyRules>"
        oma_uri = filtered_rules["oma-uri"]
        has_printing = False

        for rule in filtered_rules["all"]:

            if rule.id in rules:
                print ("Conflicting rules "+rules[rule.id].toXML()+" in "+rules[rule.id].path+" != "+rule.toXML()+" in "+rule.path)
                continue
        
            rules[rule.id] = rule
            paths.append(rule.path)
            if rule.has_printing:
                has_printing = True

            intune_ux_support += self.intune_ux.get_support_for(rule)

            rulesXML += "\n"+rule.toXML()
            groups_for_rule = self.get_groups_for_rule(rule)
            all_groups = set(groups_for_rule["gpo"]+groups_for_rule["oma-uri"])
            for group in all_groups:
                if group.id not in groups:
                    groupsXML += "\n"+group.toXML()
                    groups[group.id] = group
                    paths.append(group.path)
                    intune_ux_support += self.intune_ux.get_support_for(group)
            
            for oma_uri_group in groups_for_rule["oma-uri"]:
                oma_uri[oma_uri_group.get_oma_uri()] = IntuneCustomRow(oma_uri_group)
        

        groupsXML += "\n</Groups>"
        rulesXML += "\n</PolicyRules>"

        #remove duplicates from paths
        paths = list(set(paths))
        web_paths = []
        for path in paths:
            if str(path).startswith(".\\"):
                path = path[2:]
            path = str(path).replace("\\","/")
            web_paths.append(path)

        try:
            mac_policy = {}
            mac_error = None
            mac_policy["groups"] = mac.convert_groups(ET.fromstring(groupsXML),True)
            mac_policy["rules"] = mac.convert_rules(ET.fromstring(rulesXML),True)
        except Exception as e:
            mac.log_error("Failed to convert policy to Mac:")
            mac.log_error(str(e))
            mac_policy = None
            mac_error = str(e)
    
        #Gather result
        result["oma_uri"] = oma_uri
        result["web_paths"] = web_paths
        result["rules"] = rules
        result["groups"] = groups
        result["intune_ux_support"] = intune_ux_support
        result["groupsXML"] = groupsXML
        result["rulesXML"] = rulesXML
        result["mac_policy"] = mac_policy
        result["mac_error"] = mac_error
        result["has_printing"] = has_printing

        return result    

    def generate_csv(self,dest):
        self.groups.to_csv(dest+os.sep+"dc_groups.csv",sep="\t")
        self.policy_rules.to_csv(dest+os.sep+"dc_rules.csv",sep="\t")


    def generate_text(self,result,dest,file,title, description="A sample policy", settings = None ):
        
        if settings is not None:
            custom_settings_values = settings.getIntuneCustomValues()
            for custom_settings_value in custom_settings_values:
                result["oma_uri"][custom_settings_value] = custom_settings_values[custom_settings_value] 

        templatePath = pathlib.Path(__file__).parent.resolve()
        templateLoader = jinja2.FileSystemLoader(searchpath=templatePath)
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = args.template
        template = templateEnv.get_template(TEMPLATE_FILE)
        out = template.render(
            {"intuneCustomSettings":result["oma_uri"],
             "paths":result["web_paths"],
             "rules":result["rules"],
             "groups":result["groups"], 
             "intune_ux_support":result["intune_ux_support"],
             "groupsXML": result["groupsXML"], 
             "rulesXML":result["rulesXML"],
             "macPolicy":result["mac_policy"],
             "macError": result["mac_error"],
             "has_printing": result["has_printing"],
             "description": description,
             "settings": settings,
             "env":os.environ,
             "title":title})
        

        with open(dest+os.sep+file,"w") as out_file:
            out_file.write(out)
            out_file.close()

Default_Settings = Settings(
    {
        Setting.DefaultEnforcement: "Deny",
        Setting.DeviceControlEnabled: True
    }
)

def dir_path(string):
    paths = string.split(os.pathsep)
    for path in paths:
        if os.path.isdir(path):
            continue
        else:
            raise NotADirectoryError(path)
    return paths

def dir(path):
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)

def file(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentError("Not a file "+path)

def format(string):
    match string:
        case "text":
            return string
        case "csv":
            return string
        case other:
            raise argparse.ArgumentError("Invalid format "+string)

def parse_in_file(in_file):
    query = "path.str.contains('"+in_file+"',regex=False)"
    title = str(in_file.split(os.sep)[-1]).split(".")[0]
    outfile = title+".md"
    return query,title,outfile

def load_scenarios(scenarios_file):
     with open(scenarios_file) as file:
         scenarios = json.loads(file.read())
         return scenarios
     
def generate_readme(results,dest,title):
    templatePath = pathlib.Path(__file__).parent.resolve()
    templateLoader = jinja2.FileSystemLoader(searchpath=templatePath)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "readme.j2"
    template = templateEnv.get_template(TEMPLATE_FILE)
    out = template.render(
        {
            "results":results,
            "dest":dest,
            "title":title,
            "env":os.environ
         }
    )

    with open(dest+os.sep+"readme.md","w") as out_file:
        out_file.write(out)
        out_file.close()

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(
        description='Utility for importing/exporting device control policies.')

    
    input_group =arg_parser.add_mutually_exclusive_group()
    input_group.add_argument('-q','--query',dest="query",help='The query to retrieve the policy rules to process')
    input_group.add_argument('-s','--scenarios',dest="scenarios",type=file,help='A JSON file that contains a list of scenarios to process')
    input_group.add_argument('-i','--input',dest="in_file",type=file,help='A policy rules to process')


    arg_parser.add_argument('-p', '--path', type=dir_path, dest="source_path", help='The path to search for source files',default=".")
    arg_parser.add_argument('-f','--format',type=format, dest="format",help="The format of the output (text)",default="text")
    arg_parser.add_argument('-o','--output',dest="out_file",help="The output file")
    arg_parser.add_argument('-d','--dest',dest="dest",type=dir,help="The output directory",default=".")
    arg_parser.add_argument('-g','--generate',dest="generate_oma_uri",action="store_true",help='Generates XML for oma-uri')
    arg_parser.add_argument('-t','--template',dest="template",help="Jinja template to use to generate output",default="dcutil.j2")

    args = arg_parser.parse_args()

    inventory = Inventory(args.source_path,args.generate_oma_uri,args.dest)

    query = args.query
    title = None
    if "TITLE" in os.environ.keys():
        title = os.environ["TITLE"]

    out_file = args.out_file

    if args.scenarios is not None:
        results = {}
        scenarios = load_scenarios(args.scenarios)
        for rule in scenarios["rules"]:
            policy_file = rule["file"]
            description = "A sample policy"
            settings = Default_Settings
            title = None
            if "description" in rule.keys():
                description = rule["description"]
            if "title" in rule.keys():
                title = rule["title"]
            if "settings" in rule.keys():
                settings = Settings(rule["settings"])

            query,default_title,default_outfile = parse_in_file(policy_file)
            result = inventory.process_query(query)
            if args.format == "text":
                if title is None:
                    title = default_title
                inventory.generate_text(result,args.dest,default_outfile,title,description,settings)

            results[policy_file] = {
                "result":result,
                "title": title,
                "file": default_outfile
            }

        generate_readme(results,args.dest,scenarios["title"])


    elif query is None:
        if args.in_file is not None:
            query,title,default_outfile = parse_in_file(args.in_file)
            if out_file is None:
                out_file = default_outfile

        if args.format == "text":
            result = inventory.process_query(query)
            inventory.generate_text(result,args.dest,out_file,title)
        elif args.format == "csv":
            inventory.generate_csv(args.dest)
        