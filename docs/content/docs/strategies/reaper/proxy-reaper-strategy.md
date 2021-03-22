# strategies/reaper/ProxyReaperStrategy.vy
> vyper: `0.2.10`
> 
> 








## Events


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
        "name": "_reaper",
        "type": "address"
      },
      {
        "name": "_staker",
        "type": "address"
      },
      {
        "name": "_rewardContract",
        "type": "address"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "invest",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [],
    "gas": 5740
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "reap",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 3824
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "deposit",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [],
    "gas": 5800
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "withdraw",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      },
      {
        "name": "_account",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 4611
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "availableToDeposit",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      },
      {
        "name": "_account",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 511
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "availableToWithdraw",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      },
      {
        "name": "_account",
        "type": "address"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 541
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
    "gas": 37801
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "applyOwnership",
    "inputs": [],
    "outputs": [],
    "gas": 38657
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "reaper",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1328
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "staker",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1358
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "rewardContract",
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
    "name": "owner",
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
    "name": "futureOwner",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1448
  }
]
```

## Byte code
```bin
0x606061078d61014039602061078d60c03960c05160a01c1561002057600080fd5b6020602061078d0160c03960c05160a01c1561003b57600080fd5b6020604061078d0160c03960c05160a01c1561005657600080fd5b600061014051141515156100a9576308c379a06101a05260206101c05260126101e0527f5f726561706572206973206e6f74207365740000000000000000000000000000610200526101e05060646101bcfd5b600061016051141515156100fc576308c379a06101a05260206101c05260126101e0527f5f7374616b6572206973206e6f74207365740000000000000000000000000000610200526101e05060646101bcfd5b6000610180511415151561014f576308c379a06101a05260206101c052601a6101e0527f5f726577617264436f6e7472616374206973206e6f7420736574000000000000610200526101e05060646101bcfd5b6101405160005561016051600155610180516002553360035561077556600436101561000d57610602565b600035601c52600051341561002157600080fd5b632afcf48081141561013e576000543314151561007d576308c379a061014052602061016052600b610180527f726561706572206f6e6c790000000000000000000000000000000000000000006101a05261018050606461015cfd5b6001546101405260206102a060646323b872dd6101e052600054610200526101405161022052600435610240526101fc600060206101c060046351ed6a306101605261017c610140515afa6100d157600080fd5b601f3d116100de57600080fd5b6000506101c0515af16100f057600080fd5b601f3d116100fd57600080fd5b6000506102a050610140513b61011257600080fd5b60006000602463a694fc3a610160526004356101805261017c6000610140515af161013c57600080fd5b005b63c72896ac8114156101e1576000543314151561019a576308c379a061014052602061016052600b610180527f726561706572206f6e6c790000000000000000000000000000000000000000006101a05261018050606461015cfd5b60206101c06024631e83409a610140526002546101605261015c60006001545af16101c457600080fd5b601f3d116101d157600080fd5b6000506101c05160005260206000f35b63b6b55f258114156102fe576000543314151561023d576308c379a061014052602061016052600b610180527f726561706572206f6e6c790000000000000000000000000000000000000000006101a05261018050606461015cfd5b6001546101405260206102a060646323b872dd6101e052600054610200526101405161022052600435610240526101fc600060206101c060046351ed6a306101605261017c610140515afa61029157600080fd5b601f3d1161029e57600080fd5b6000506101c0515af16102b057600080fd5b601f3d116102bd57600080fd5b6000506102a050610140513b6102d257600080fd5b60006000602463a694fc3a610160526004356101805261017c6000610140515af16102fc57600080fd5b005b62f714ce8114156103a85760243560a01c1561031957600080fd5b60005433141515610369576308c379a061014052602061016052600b610180527f726561706572206f6e6c790000000000000000000000000000000000000000006101a05261018050606461015cfd5b6001543b61037657600080fd5b600060006044638381e18261014052600435610160526024356101805261015c60006001545af16103a657600080fd5b005b63b5ec3e408114156103d05760243560a01c156103c457600080fd5b60043560005260206000f35b63917564b58114156103f85760243560a01c156103ec57600080fd5b60043560005260206000f35b63f2fde38b81141561049a5760043560a01c1561041457600080fd5b60035433141515610464576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b600435600455600435610140527f2f56810a6bf40af059b96d3aea4db54081f378029a518390491093a7b67032e96020610140a1005b630119020781141561058857600354331415156104f6576308c379a061014052602061016052600a610180527f6f776e6572206f6e6c79000000000000000000000000000000000000000000006101a05261018050606461015cfd5b6004546101405260006101405114151515610550576308c379a061016052602061018052600d6101a0527f6f776e6572206e6f7420736574000000000000000000000000000000000000006101c0526101a050606461017cfd5b6101405160035561014051610160527febee2d5739011062cb4f14113f3b36bf0ffe3da5c0568f64189d1012a11891056020610160a1005b631121e3e18114156105a05760005460005260206000f35b635ebaf1db8114156105b85760015460005260206000f35b636ea69d628114156105d05760025460005260206000f35b638da5cb5b8114156105e85760035460005260206000f35b63b9e9d1aa8114156106005760045460005260206000f35b505b60006000fd5b61016d6107750361016d60003961016d610775036000f3
```