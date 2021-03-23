# testing/ControllerMock.vy
> vyper: `0.2.10`
> 
> 










## Methods



## ABI
```json
[
  {
    "stateMutability": "nonpayable",
    "type": "constructor",
    "inputs": [],
    "outputs": []
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "farmToken",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 288
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "addReaper",
    "inputs": [
      {
        "name": "_reaper",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 163559
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "removeReaper",
    "inputs": [
      {
        "name": "_reaper",
        "type": "address"
      }
    ],
    "outputs": [],
    "gas": 403
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "claimAdminFee",
    "inputs": [
      {
        "name": "_reaper",
        "type": "address"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "claimAdminFee",
    "inputs": [
      {
        "name": "_reaper",
        "type": "address"
      },
      {
        "name": "_gasToken",
        "type": "address"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "reapers",
    "inputs": [
      {
        "name": "arg0",
        "type": "uint256"
      }
    ],
    "outputs": [
      {
        "name": "",
        "type": "address"
      }
    ],
    "gas": 1317
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "indexByReaper",
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
    "gas": 1453
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "lastReaperIndex",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1268
  }
]
```

## Byte code
```bin
0x61023256600436101561000d57610228565b600035601c52600051341561002157600080fd5b63c2442f9381141561003857600060005260206000f35b63f8ad06fe81141561012e576003541561005157600080fd5b600160035560043560a01c1561006657600080fd5b600160043560e05260c052604060c0205461014052610140511515156100cb576308c379a061016052602061018052600d6101a0527f72656170657220657869737473000000000000000000000000000000000000006101c0526101a050606461017cfd5b60025460018181830110156100df57600080fd5b8082019050905061016052600435610160516103e881106100ff57600080fd5b600060c052602060c020015561016051600160043560e05260c052604060c02055610160516002556000600355005b637ef012cd81141561014c5760043560a01c1561014a57600080fd5b005b631c48e98181141561016357600061014052610194565b637d1b56e581141561018f5760243560a01c1561017f57600080fd5b6020602461014037600050610194565b6101a6565b60043560a01c156101a457600080fd5b005b639fc71c068114156101d8576004356103e881106101c357600080fd5b600060c052602060c020015460005260206000f35b637a99368581141561020e5760043560a01c156101f457600080fd5b600160043560e05260c052604060c0205460005260206000f35b63df0b97fd8114156102265760025460005260206000f35b505b60006000fd5b61000461023203610004600039610004610232036000f3
```