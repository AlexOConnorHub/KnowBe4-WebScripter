# KnowBe4 Automation Script

This is just a script that uses selenium to help automate mass creation.

## Config

By defualt, this expects a file `config.json` (but this can be specified by `--config-file`). A sample file would look like

```json
{
    {
    "username": "<email>",
    "password": "<password>",
    "totp": "<totp_secret>",
    "todo": [
        {
            "menuText": "USERS",
            "tabText": "Groups",
            "uri": "/ui/users/groups",
            "buttonText": "Create New Group",
            "data": [
                [
                    {
                        "id": "__BVID__7097",
                        "value": "GROUP_NAME"
                    },
                    {
                        "id": "__BVID__7104",
                        "click": true
                    }
                ]
            ]
        }
    ]
}
}
```

### Options

#### Authentication

Providing the flag `--wait-for-auth` will cause the script to wait for the user to authenticate before continuing. The other option would be to privde the following keys in the config file

- username: username for user
- password: password for user

If you have TOTP enabled, the script will wait for you to enter the code before continuing. If you want to automate this, you can provide the following key in the config file

- totp: if TOTP is enabled, the secret can be provided here to automate logging in.

#### Todo

The `todo` key is an array of objects that will be done. Each object has the following keys

- uri: the uri to navigate to
- buttonText: the text of the button to click on
<!-- - TODO: Add dropdown selection key -->
- data: the data to be added (see below)

##### Data

The `data` key is a list of items to be added. This key consists of an array of arrays of objects. Below is an example with "comments". If you intend to copy/paste this, remove "#..." from the file.

```json
... 
"data": [ # Holds items to be added
    [ # This is one item to be added
        { # This is one attribute
            "id": "__BVID__7097",
            "value": "GROUP_NAME"
        },
        { # This is another
            "id": "__BVID__7104",
            "click": true
        }
    ],
    [ # This is another item to be added
        ...
]
...
```

The documentation here provides a list of keys for the attributes.

- id: the id of the element to be modified
- name: the name of the element to be modified
- xpath: the xpath of the element to be modified
- class_name: the class name of the element to be modified
- css_selector: the css selector of the element to be modified
- link_text: the link text of the element to be modified
- partial_link_text: the partial link text of the element to be modified
- value: the value to be set
- click: if this is set to true, the element will be clicked
