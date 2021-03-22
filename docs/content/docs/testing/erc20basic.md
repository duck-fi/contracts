# testing/ERC20Basic.vy
> vyper: `0.2.10`
> 
> 








## Events


{{< hint info >}}
**Transfer**

* `_from` : address, *indexed*
* `_to` : address, *indexed*
* `_value` : uint256, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**Approval**

* `_owner` : address, *indexed*
* `_spender` : address, *indexed*
* `_value` : uint256, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**CommitOwnership**

* `admin` : address, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**ApplyOwnership**

* `admin` : address, *notIndexed*
{{< /hint >}}


## Methods



## ABI
```json
[
  {
    "name": "Transfer",
    "inputs": [
      {
        "name": "_from",
        "type": "address",
        "indexed": true
      },
      {
        "name": "_to",
        "type": "address",
        "indexed": true
      },
      {
        "name": "_value",
        "type": "uint256",
        "indexed": false
      }
    ],
    "anonymous": false,
    "type": "event"
  },
  {
    "name": "Approval",
    "inputs": [
      {
        "name": "_owner",
        "type": "address",
        "indexed": true
      },
      {
        "name": "_spender",
        "type": "address",
        "indexed": true
      },
      {
        "name": "_value",
        "type": "uint256",
        "indexed": false
      }
    ],
    "anonymous": false,
    "type": "event"
  },
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
    "inputs": [
      {
        "name": "_name",
        "type": "string"
      },
      {
        "name": "_symbol",
        "type": "string"
      },
      {
        "name": "_decimals",
        "type": "uint256"
      },
      {
        "name": "_supply",
        "type": "uint256"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "totalSupply",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1088
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "allowance",
    "inputs": [
      {
        "name": "_owner",
        "type": "address"
      },
      {
        "name": "_spender",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1548
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transfer",
    "inputs": [
      {
        "name": "_to",
        "type": "address"
      },
      {
        "name": "_value",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 74770
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transferFrom",
    "inputs": [
      {
        "name": "_from",
        "type": "address"
      },
      {
        "name": "_to",
        "type": "address"
      },
      {
        "name": "_value",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 111125
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "approve",
    "inputs": [
      {
        "name": "_spender",
        "type": "address"
      },
      {
        "name": "_value",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 37851
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "setMinter",
    "inputs": [
      {
        "name": "_minter",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 36440
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "mint",
    "inputs": [
      {
        "name": "account",
        "type": "address"
      },
      {
        "name": "amount",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 75776
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "burn",
    "inputs": [
      {
        "name": "amount",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 74696
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transferOwnership",
    "inputs": [
      {
        "name": "_future_owner",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 37861
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "applyOwnership",
    "inputs": [],
    "outputs": [],
    "gas": 38717
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "name",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "gas": 7790
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "symbol",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "string"
      }
    ],
    "gas": 6843
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "decimals",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1448
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "balanceOf",
    "inputs": [
      {
        "name": "arg0",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1693
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "minter",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1508
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
    "gas": 1538
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "future_owner",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1568
  }
]
```

## Byte code
```bin
0x6080610992610140396060602061099260c03960c051610992016101c0396040602061099260c03960c05160040135111561003957600080fd5b6040602060206109920160c03960c05161099201610240396020602060206109920160c03960c05160040135111561007057600080fd5b6101c080600060c052602060c020602082510161012060006003818352015b826101205160200211156100a2576100c4565b61012051602002850151610120518501555b815160010180835281141561008f575b50505050505061024080600160c052602060c020602082510161012060006002818352015b826101205160200211156100fc5761011e565b61012051602002850151610120518501555b81516001018083528114156100e9575b505050505050610180516002556101a051604e610180511061013f57600080fd5b61018051600a0a808202821582848304141761015a57600080fd5b809050905090506102a0526102a05160033360e05260c052604060c020556102a05160055533600655336007556102a0516102c0523360007fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef60206102c0a361097a56600436101561000d576107b6565b600035601c52600051341561002157600080fd5b6318160ddd8114156100395760055460005260206000f35b63dd62ed3e81141561008d5760043560a01c1561005557600080fd5b60243560a01c1561006557600080fd5b600460043560e05260c052604060c02060243560e05260c052604060c0205460005260206000f35b63a9059cbb81141561013e5760043560a01c156100a957600080fd5b60033360e05260c052604060c0208054602435808210156100c957600080fd5b80820390509050815550600360043560e05260c052604060c02080546024358181830110156100f757600080fd5b8082019050905081555060243561014052600435337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b6323b872dd81141561023b5760043560a01c1561015a57600080fd5b60243560a01c1561016a57600080fd5b600360043560e05260c052604060c02080546044358082101561018c57600080fd5b80820390509050815550600360243560e05260c052604060c02080546044358181830110156101ba57600080fd5b80820190509050815550600460043560e05260c052604060c0203360e05260c052604060c0208054604435808210156101f257600080fd5b80820390509050815550604435610140526024356004357fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b63095ea7b38114156102b45760043560a01c1561025757600080fd5b60243560043360e05260c052604060c02060043560e05260c052604060c0205560243561014052600435337f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b9256020610140a3600160005260206000f35b63fca3b5aa8114156102ef5760043560a01c156102d057600080fd5b60065433146102de57600080fd5b600435600655600160005260206000f35b6340c10f198114156103b45760043560a01c1561030b57600080fd5b600654331461031957600080fd5b60006004351861032857600080fd5b6005805460243581818301101561033e57600080fd5b80820190509050815550600360043560e05260c052604060c020805460243581818301101561036c57600080fd5b808201905090508155506024356101405260043560007fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b6342966c688114156104445760058054600435808210156103d457600080fd5b8082039050905081555060033360e05260c052604060c0208054600435808210156103fe57600080fd5b80820390509050815550600435610140526000337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b63f2fde38b8114156104e65760043560a01c1561046057600080fd5b600754331415156104b0576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600855600435610140527f2f56810a6bf40af059b96d3aea4db54081f378029a518390491093a7b67032e96020610140a1005b63011902078114156105d45760075433141515610542576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600854610140526000610140511415151561059c576308c379a061016052602061018052600d6101a0527f6f776e6572206e6f7420736574000000000000000000000000000000000000006101c0526101a050606461017cfd5b6101405160075561014051610160527febee2d5739011062cb4f14113f3b36bf0ffe3da5c0568f64189d1012a11891056020610160a1005b6306fdde038114156106795760008060c052602060c020610180602082540161012060006003818352015b8261012051602002111561061257610634565b61012051850154610120516020028501525b81516001018083528114156105ff575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b6395d89b4181141561071e5760018060c052602060c020610180602082540161012060006002818352015b826101205160200211156106b7576106d9565b61012051850154610120516020028501525b81516001018083528114156106a4575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b63313ce5678114156107365760025460005260206000f35b6370a0823181141561076c5760043560a01c1561075257600080fd5b600360043560e05260c052604060c0205460005260206000f35b63075461728114156107845760065460005260206000f35b638da5cb5b81141561079c5760075460005260206000f35b631ec0cdc18114156107b45760085460005260206000f35b505b60006000fd5b6101be61097a036101be6000396101be61097a036000f3
```