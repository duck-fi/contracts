# tokens/FarmToken.vy
> vyper: `0.2.10`
> author: `Dispersion Finance Team`
> license: `MIT`


**Dispersion Farm Token**



Based on the ERC-20 token standard as defined at https://eips.ethereum.org/EIPS/eip-20. Emission is halved every year.



*ERC20 token with linear mining supply, rate changes every year*



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

{{< hint info >}}
**YearEmissionUpdate**

* `newYearEmission` : uint256, *notIndexed*
{{< /hint >}}


## Methods

### __init__
> type: `nonpayable constructor`
> 


Contract constructor    


*Premine emission is returnted to deployer*


Arguments:
    
* `_name`:  - *Token full name*
    
* `_symbol`:  - *Token symbol*
    





### decimals
> type: `view function`
> gas: `288`


Returns token decimals value    


*For ERC20 compatibility*



Returns:

* `_0` - Token decimals





### setName
> type: `nonpayable function`
> gas: `142531`


Changes token name and symbol    


*Callable by owner only*


Arguments:
    
* `_name`:  - *Token full name*
    
* `_symbol`:  - *Token symbol*
    





### setMinter
> type: `nonpayable function`
> gas: `36448`


Sets minter contract address    


*Callable by owner only*


Arguments:
    
* `_minter`:  - *Minter contract which allowed to mint for new tokens*
    





### mint
> type: `nonpayable function`
> gas: `298974`


Mints new tokens for account `_account` with amount `_amount`    


*Callable by minter only*


Arguments:
    
* `_account`:  - *Account to mint tokens for*
    
* `_amount`:  - *Amount to mint*
    





### startEmission
> type: `nonpayable function`
> gas: `108550`


Starts token emission    


*Callable by owner only*






### transfer
> type: `nonpayable function`
> gas: `75046`


Transfers `_amount` of tokens from `msg.sender` to `_recipient` address    


*ERC20 function*


Arguments:
    
* `_recipient`:  - *Account to send tokens to*
    
* `_amount`:  - *Amount to send*
    


Returns:

* `_0` - Boolean success value





### transferFrom
> type: `nonpayable function`
> gas: `111799`


Transfers `_amount` of tokens from `_sender` to `_recipient` address    


*ERC20 function. Allowance from `_sender` to `msg.sender` is needed*


Arguments:
    
* `_sender`:  - *Account to send tokens from*
    
* `_recipient`:  - *Account to send tokens to*
    
* `_amount`:  - *Amount to send*
    


Returns:

* `_0` - Boolean success value





### approve
> type: `nonpayable function`
> gas: `39192`


Approves allowance from `msg.sender` to `_spender` address for `_amount` of tokens    


*ERC20 function*


Arguments:
    
* `_spender`:  - *Allowed account to send tokens from `msg.sender`*
    
* `_amount`:  - *Allowed amount to send tokens from `msg.sender`*
    


Returns:

* `_0` - Boolean success value





### burn
> type: `nonpayable function`
> gas: `74741`


Burns `_amount` of tokens from `msg.sender`    



Arguments:
    
* `_amount`:  - *Amount to burn*
    





### transferOwnership
> type: `nonpayable function`
> gas: `37951`


Transfers ownership by setting new owner `_futureOwner` candidate    


*Callable by owner only*


Arguments:
    
* `_futureOwner`:  - *Future owner address*
    





### applyOwnership
> type: `nonpayable function`
> gas: `38807`


Applies transfer ownership    


*Callable by owner only. Function call actually changes owner*






### yearEmission
> type: `nonpayable function`
> gas: `110487`


Updates emission per year value    







### emissionIntegral
> type: `nonpayable function`
> gas: `223279`


Updates current emission integral (max total supply at block.timestamp)    









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
    "name": "YearEmissionUpdate",
    "inputs": [
      {
        "name": "newYearEmission",
        "type": "uint256",
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
    "name": "setMinter",
    "inputs": [
      {
        "name": "_minter",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 36448
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
    "gas": 298974
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "startEmission",
    "inputs": [],
    "outputs": [],
    "gas": 108550
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "yearEmission",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 110487
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "emissionIntegral",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 223279
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
    "gas": 75046
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
    "gas": 111799
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
    "gas": 39192
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
    "gas": 74741
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
    "gas": 37951
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "applyOwnership",
    "inputs": [],
    "outputs": [],
    "gas": 38807
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
    "gas": 1478
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
    "gas": 1508
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
    "gas": 1538
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
    "gas": 6993
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
    "gas": 7023
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
    "gas": 1843
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
    "gas": 1658
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "allowance",
    "inputs": [
      {
        "name": "arg0",
        "type": "address"
      },
      {
        "name": "arg1",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 2118
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "startEmissionTimestamp",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1718
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "lastEmissionUpdateTimestamp",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1748
  }
]
```

## Byte code
```bin
0x60406110f761014039604060206110f760c03960c0516110f70161018039602060206110f760c03960c05160040135111561003957600080fd5b6028602060206110f70160c03960c0516110f7016101e0396008602060206110f70160c03960c05160040135111561007057600080fd5b61018080600360c052602060c020602082510161012060006002818352015b826101205160200211156100a2576100c4565b61012051602002850151610120518501555b815160010180835281141561008f575b5050505050506101e080600460c052602060c020602082510161012060006002818352015b826101205160200211156100fc5761011e565b61012051602002850151610120518501555b81516001018083528114156100e9575b5050505050506955c3180fea093320000060053360e05260c052604060c020556955c3180fea0933200000600655336000556955c3180fea0933200000610240523360007fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610240a36110df56600436101561000d57610de2565b600035601c52600051341561002157600080fd5b63313ce56781141561003857601260005260206000f35b635c707f0781141561018a57604060043560040161014037602060043560040135111561006457600080fd5b60286024356004016101a037600860243560040135111561008457600080fd5b600054331415156100d4576308c379a061020052602061022052600a610240527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006102605261024050606461021cfd5b61014080600360c052602060c020602082510161012060006002818352015b8261012051602002111561010657610128565b61012051602002850151610120518501555b81516001018083528114156100f3575b5050505050506101a080600460c052602060c020602082510161012060006002818352015b8261012051602002111561016057610182565b61012051602002850151610120518501555b815160010180835281141561014d575b505050505050005b63fca3b5aa8114156102505760043560a01c156101a657600080fd5b600054331415156101f6576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600060043514151515610248576308c379a061014052602061016052600c610180527f7a65726f206164647265737300000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600255005b6340c10f1981141561043c5760043560a01c1561026c57600080fd5b600254331415156102bc576308c379a061014052602061016052600b610180527f6d696e746572206f6e6c790000000000000000000000000000000000000000006101a05261018050606461015cfd5b60006004351415151561030e576308c379a061014052602061016052600c610180527f7a65726f206164647265737300000000000000000000000000000000000000006101a05261018050606461015cfd5b600654610140526101405160243581818301101561032b57600080fd5b80820190509050600655600560043560e05260c052604060c020805460243581818301101561035957600080fd5b808201905090508155506101405160243581818301101561037957600080fd5b808201905090506101405160065801610ec0565b6101605261014052610160516955c3180fea09332000008181830110156103b357600080fd5b8082019050905010151515610407576308c379a06101805260206101a052601d6101c0527f6578636565647320616c6c6f7761626c65206d696e7420616d6f756e740000006101e0526101c050606461019cfd5b6024356101605260043560007fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610160a3005b63bcccf8888114156105355760005433141515610498576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b6009541515156104e7576308c379a0610140526020610160526018610180527f656d697373696f6e20616c7265616479207374617274656400000000000000006101a05261018050606461015cfd5b69d3c21bcecceda1000000600a55426009554260085569d3c21bcecceda1000000610140527f640a060bdae1d7e3074eec961059fbe88aaa1a79d77a7f3a4dc980c051c641ad6020610140a1005b63edc8687f81141561055b5760065801610de8565b610140526101405160005260206000f35b6314fe1c048114156105815760065801610ec0565b610140526101405160005260206000f35b63a9059cbb8114156106845760043560a01c1561059d57600080fd5b6000600435141515156105ef576308c379a0610140526020610160526019610180527f726563697069656e74206973207a65726f2061646472657373000000000000006101a05261018050606461015cfd5b60053360e05260c052604060c02080546024358082101561060f57600080fd5b80820390509050815550600560043560e05260c052604060c020805460243581818301101561063d57600080fd5b8082019050905081555060243561014052600435337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3600160005260206000f35b6323b872dd8114156108725760043560a01c156106a057600080fd5b60243560a01c156106b057600080fd5b600060043514151515610702576308c379a0610140526020610160526016610180527f73656e646572206973207a65726f2061646472657373000000000000000000006101a05261018050606461015cfd5b600060243514151515610754576308c379a0610140526020610160526019610180527f726563697069656e74206973207a65726f2061646472657373000000000000006101a05261018050606461015cfd5b600560043560e05260c052604060c02080546044358082101561077657600080fd5b80820390509050815550600560243560e05260c052604060c02080546044358181830110156107a457600080fd5b80820190509050815550600760043560e05260c052604060c0203360e05260c052604060c02054610140527fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff61014051181561083357610140516044358082101561080e57600080fd5b80820390509050600760043560e05260c052604060c0203360e05260c052604060c020555b604435610160526024356004357fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610160a3600160005260206000f35b63095ea7b38114156109655760043560a01c1561088e57600080fd5b602435151561089e5760016108bd565b60073360e05260c052604060c02060043560e05260c052604060c02054155b1515610908576308c379a0610140526020610160526010610180527f616c726561647920617070726f766564000000000000000000000000000000006101a05261018050606461015cfd5b60243560073360e05260c052604060c02060043560e05260c052604060c0205560243561014052600435337f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b9256020610140a3600160005260206000f35b6342966c688114156109ec57600680546004358082101561098557600080fd5b8082039050905081555060053360e05260c052604060c0208054600435808210156109af57600080fd5b80820390509050815550600435610140526000337fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef6020610140a3005b63f2fde38b811415610a8e5760043560a01c15610a0857600080fd5b60005433141515610a58576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600155600435610140527f2f56810a6bf40af059b96d3aea4db54081f378029a518390491093a7b67032e96020610140a1005b6301190207811415610b7c5760005433141515610aea576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b6001546101405260006101405114151515610b44576308c379a061016052602061018052600d6101a0527f6f776e6572206e6f7420736574000000000000000000000000000000000000006101c0526101a050606461017cfd5b6101405160005561014051610160527febee2d5739011062cb4f14113f3b36bf0ffe3da5c0568f64189d1012a11891056020610160a1005b638da5cb5b811415610b945760005460005260206000f35b63b9e9d1aa811415610bac5760015460005260206000f35b6307546172811415610bc45760025460005260206000f35b6306fdde03811415610c695760038060c052602060c020610180602082540161012060006002818352015b82610120516020021115610c0257610c24565b61012051850154610120516020028501525b8151600101808352811415610bef575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b6395d89b41811415610d0e5760048060c052602060c020610180602082540161012060006002818352015b82610120516020021115610ca757610cc9565b61012051850154610120516020028501525b8151600101808352811415610c94575b50505050505061018051806101a001818260206001820306601f82010390500336823750506020610160526040610180510160206001820306601f8201039050610160f35b6370a08231811415610d445760043560a01c15610d2a57600080fd5b600560043560e05260c052604060c0205460005260206000f35b6318160ddd811415610d5c5760065460005260206000f35b63dd62ed3e811415610db05760043560a01c15610d7857600080fd5b60243560a01c15610d8857600080fd5b600760043560e05260c052604060c02060243560e05260c052604060c0205460005260206000f35b6340c57d46811415610dc85760085460005260206000f35b63cdafa649811415610de05760095460005260206000f35b505b60006000fd5b6101405260095461016052610160511515610e0b57600060005260005161014051565b610160516301e13380818183011015610e2357600080fd5b8082019050905061018052600a546101a05261018051421115610eb057600b80546101a051818183011015610e5757600080fd5b80820190509050815550610180516009556101a080516002808204905090508152506101a051600a556101a0516101c0527f640a060bdae1d7e3074eec961059fbe88aaa1a79d77a7f3a4dc980c051c641ad60206101c0a15b6101a05160005260005161014051565b61014052610140516101605160065801610de8565b6101805261016052610140526101805161016052600b54610160514260095480821015610f0157600080fd5b808203905090508082028215828483041417610f1c57600080fd5b809050905090506301e1338080820490509050818183011015610f3e57600080fd5b8082019050905060005260005161014051565b61018e6110df0361018e60003961018e6110df036000f3
```