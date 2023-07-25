# myoboku
Picsellia Job launcher and emulator

```
sequenceDiagram
    participant Hinokuni
    participant Myoboku
    participant Vault
    participant Docker Server
    Myoboku->>+Hinokuni: register
    Hinokuni-->>-Myoboku: return (api_token, vault_creds)
    Hinokuni->>+Myoboku: launch
    Myoboku->>+Vault: /secrets/docker
    Vault-->>-Myoboku: return (docker_creds)
    Myoboku->>+Docker Server: run <docker_image_name>
    Docker Server--)Myoboku: pull done, running detached
```
