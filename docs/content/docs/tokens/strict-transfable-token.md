# tokens/StrictTransfableToken.vy
> vyper: `0.2.10`
> 
> 








## Events


{{< hint info >}}
**Transfer**

* `sender` : address, *indexed*
* `receiver` : address, *indexed*
* `value` : uint256, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**Approval**

* `owner` : address, *indexed*
* `spender` : address, *indexed*
* `value` : uint256, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**CommitOwnership**

* `owner` : address, *notIndexed*
{{< /hint >}}

{{< hint info >}}
**ApplyOwnership**

* `owner` : address, *notIndexed*
{{< /hint >}}


## Methods



## ABI
```json
[
  {
    "name": "Transfer",
    "inputs": [
      {
        "name": "sender",
        "type": "address",
        "indexed": true
      },
      {
        "name": "receiver",
        "type": "address",
        "indexed": true
      },
      {
        "name": "value",
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
        "name": "owner",
        "type": "address",
        "indexed": true
      },
      {
        "name": "spender",
        "type": "address",
        "indexed": true
      },
      {
        "name": "value",
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
        "name": "owner",
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
        "name": "owner",
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
        "name": "_mintersCheckList",
        "type": "address"
      },
      {
        "name": "_transfableAccount",
        "type": "address"
      }
    ],
    "outputs": []
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
    "gas": 288
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "setName",
    "inputs": [
      {
        "name": "_name",
        "type": "string"
      },
      {
        "name": "_symbol",
        "type": "string"
      }
    ],
    "outputs": [],
    "gas": 142531
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "mint",
    "inputs": [
      {
        "name": "_account",
        "type": "address"
      },
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [],
    "gas": 75984
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transfer",
    "inputs": [
      {
        "name": "_recipient",
        "type": "address"
      },
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 76684
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "transferFrom",
    "inputs": [
      {
        "name": "_sender",
        "type": "address"
      },
      {
        "name": "_recipient",
        "type": "address"
      },
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 76085
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
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "bool"
      }
    ],
    "gas": 538
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "allowance",
    "inputs": [
      {
        "name": "_sender",
        "type": "address"
      },
      {
        "name": "_recipient",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 668
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "burn",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [],
    "gas": 74651
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
    "name": "owner",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1388
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
    "gas": 1418
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "mintersCheckList",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1448
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "transfableAccount",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1478
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
    "gas": 6933
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
    "gas": 6963
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
    "gas": 1783
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
    "gas": 1598
  }
]
```

## Byte code
```bin
0x6080610cc46101403960406020610cc460c03960c051610cc4016101c03960206020610cc460c03960c05160040135111561003957600080fd5b602860206020610cc40160c03960c051610cc40161022039600860206020610cc40160c03960c05160040135111561007057600080fd5b60206040610cc40160c03960c05160a01c1561008b57600080fd5b60206060610cc40160c03960c05160a01c156100a657600080fd5b600061018051141515156100f9576308c379a06102805260206102a052601b6102c0527f6d696e74657273436865636b4c697374206973206e6f742073657400000000006102e0526102c050606461029cfd5b60006101a0511415151561014c576308c379a06102805260206102a05260116102c0527f63616c6c6572206973206e6f74207365740000000000000000000000000000006102e0526102c050606461029cfd5b6101c080600460c052602060c020602082510161012060006002818352015b8261012051602002111561017e576101a0565b61012051602002850151610120518501555b815160010180835281141561016b575b50505050505061022080600560c052602060c020602082510161012060006002818352015b826101205160200211156101d8576101fa565b61012051602002850151610120518501555b81516001018083528114156101c5575b50505050505033600055610180516002556101a051600355610cac56600436101561000d57610a8f565b600035601c52600051341561002157600080fd5b63313ce56781141561003857601260005260206000f35b635c707f0781141561018a57604060043560040161014037602060043560040135111561006457600080fd5b60286024356004016101a037600860243560040135111561008457600080fd5b600054331415156100d4576308c379a061020052602061022052600a610240527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006102605261024050606461021cfd5b61014080600460c052602060c020602082510161012060006002818352015b8261012051602002111561010657610128565b61012051602002850151610120518501555b81516001018083528114156100f3575b5050505050506101a080600560c052602060c020602082510161012060006002818352015b8261012051602002111561016057610182565b61012051602002850151610120518501555b815160010180835281141561014d575b505050505050005b6340c10f198114156103005760043560a01c156101a657600080fd5b60206101c0602463c2bc2efc61014052336101605261015c6002545afa6101cc57600080fd5b601f3d116101d957600080fd5b6000506101c051151561022b576308c379a06101e052602061020052600b610220527f6d696e746572206f6e6c79000000000000000000000000000000000000000000610240526102205060646101fcfd5b60006004351415151561027d576308c379a061014052602061016052600c610180527f7a65726f206164647265737300000000000000000000000000000000000000006101a05261018050606461015cfd5b6007805460243581818301101561029357600080fd5b80820190509050815550600660043560e05260c052604060c02080546024358181830110156102c157600080fd5b808201905090508155506024356101405260043560007fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3005b63a9059cbb8114156104675760043560a01c1561031c57600080fd5b60006004351415151561036e576308c379a0610140526020610160526019610180527f726563697069656e74206973207a65726f2061646472657373000000000000006101a05261018050606461015cfd5b60035433141561037f576001610387565b600354600435145b15156103d2576308c379a061014052602061016052600f610180527f737472696374207472616e7366657200000000000000000000000000000000006101a05261018050606461015cfd5b60063360e05260c052604060c0208054602435808210156103f257600080fd5b80820390509050815550600660043560e05260c052604060c020805460243581818301101561042057600080fd5b8082019050905081555060243561014052600435337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b6323b872dd8114156106205760043560a01c1561048357600080fd5b60243560a01c1561049357600080fd5b6000600435141515156104e5576308c379a0610140526020610160526016610180527f73656e646572206973207a65726f2061646472657373000000000000000000006101a05261018050606461015cfd5b600060243514151515610537576308c379a0610140526020610160526019610180527f726563697069656e74206973207a65726f2061646472657373000000000000006101a05261018050606461015cfd5b60035433141515610587576308c379a061014052602061016052600f610180527f737472696374207472616e7366657200000000000000000000000000000000006101a05261018050606461015cfd5b600660043560e05260c052604060c0208054604435808210156105a957600080fd5b80820390509050815550600660243560e05260c052604060c02080546044358181830110156105d757600080fd5b80820190509050815550604435610140526024356004357fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b63095ea7b38114156106475760043560a01c1561063c57600080fd5b600060005260206000f35b63dd62ed3e81141561067e5760043560a01c1561066357600080fd5b60243560a01c1561067357600080fd5b600060005260206000f35b6342966c6881141561070557600780546004358082101561069e57600080fd5b8082039050905081555060063360e05260c052604060c0208054600435808210156106c857600080fd5b80820390509050815550600435610140526000337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3005b63f2fde38b8114156107a75760043560a01c1561072157600080fd5b60005433141515610771576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600155600435610140527f2f56810a6bf40af059b96d3aea4db54081f378029a518390491093a7b67032e96020610140a1005b63011902078114156108955760005433141515610803576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600154610140526000610140511415151561085d576308c379a061016052602061018052600d6101a0527f6f776e6572206e6f7420736574000000000000000000000000000000000000006101c0526101a050606461017cfd5b6101405160005561014051610160527febee2d5739011062cb4f14113f3b36bf0ffe3da5c0568f64189d1012a11891056020610160a1005b638da5cb5b8114156108ad5760005460005260206000f35b63b9e9d1aa8114156108c55760015460005260206000f35b632fd928f08114156108dd5760025460005260206000f35b6377c829088114156108f55760035460005260206000f35b6306fdde0381141561099a5760048060c052602060c020610180602082540161012060006002818352015b8261012051602002111561093357610955565b61012051850154610120516020028501525b8151600101808352811415610920575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b6395d89b41811415610a3f5760058060c052602060c020610180602082540161012060006002818352015b826101205160200211156109d8576109fa565b61012051850154610120516020028501525b81516001018083528114156109c5575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b6370a08231811415610a755760043560a01c15610a5b57600080fd5b600660043560e05260c052604060c0205460005260206000f35b6318160ddd811415610a8d5760075460005260206000f35b505b60006000fd5b610217610cac03610217600039610217610cac036000f3
```