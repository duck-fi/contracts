# AddressesCheckList.vy
> vyper: `0.2.10`
> 
> 








## Events


{{< hint info >}}
**CommitOwnership**

* `admin` : address, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**ApplyOwnership**

* `admin` : address, *notIndexed*
{{< /hint >}}


## Methods

### transferOwnership
> type: `nonpayable function`
> gas: `37651`


Sets new future owner address    


*Callable by owner only*


Arguments:
    
* `_futureOwner`:  - *New future owner address*
    





### applyOwnership
> type: `nonpayable function`
> gas: `38507`


Applies new future owner address as current owner    


*Callable by owner only*






### __init__
> type: `nonpayable constructor`
> 


Contract constructor    









## ABI
```json
[
  {
    "name": "CommitOwnership",
    "inputs": [
      {
        "name": "admin",
        "type": "address",
        "indexed": false
      }
    ],
    "anonymous": false,
    "type": "event"
  },
  {
    "name": "ApplyOwnership",
    "inputs": [
      {
        "name": "admin",
        "type": "address",
        "indexed": false
      }
    ],
    "anonymous": false,
    "type": "event"
  },
  {
    "stateMutability": "nonpayable",
    "type": "constructor",
    "inputs": [],
    "outputs": []
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "set",
    "inputs": [
      {
        "name": "_key",
        "type": "address"
      },
      {
        "name": "_value",
        "type": "bool"
      }
    ],
    "outputs": [],
    "gas": 36603
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transferOwnership",
    "inputs": [
      {
        "name": "_futureOwner",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 37651
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "applyOwnership",
    "inputs": [],
    "outputs": [],
    "gas": 38507
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "owner",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1178
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "futureOwner",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1208
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "get",
    "inputs": [
      {
        "name": "arg0",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 1453
  }
]
```

## Byte code
```bin
0x3360005561030b56600436101561000d576102fd565b600035601c52600051341561002157600080fd5b6335e3b25a8114156101055760043560a01c1561003d57600080fd5b60243560011c1561004d57600080fd5b6000543314151561009d576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b6000600435141515156100ef576308c379a061014052602061016052600c610180527f7a65726f206164647265737300000000000000000000000000000000000000006101a05261018050606461015cfd5b602435600260043560e05260c052604060c02055005b63f2fde38b8114156101a75760043560a01c1561012157600080fd5b60005433141515610171576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600155600435610140527f2f56810a6bf40af059b96d3aea4db54081f378029a518390491093a7b67032e96020610140a1005b63011902078114156102955760005433141515610203576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600154610140526000610140511415151561025d576308c379a061016052602061018052600d6101a0527f6f776e6572206e6f7420736574000000000000000000000000000000000000006101c0526101a050606461017cfd5b6101405160005561014051610160527febee2d5739011062cb4f14113f3b36bf0ffe3da5c0568f64189d1012a11891056020610160a1005b638da5cb5b8114156102ad5760005460005260206000f35b63b9e9d1aa8114156102c55760015460005260206000f35b63c2bc2efc8114156102fb5760043560a01c156102e157600080fd5b600260043560e05260c052604060c0205460005260206000f35b505b60006000fd5b61000861030b0361000860003961000861030b036000f3
```