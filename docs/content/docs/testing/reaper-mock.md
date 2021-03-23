# testing/ReaperMock.vy
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
    "inputs": [
      {
        "name": "_lpToken",
        "type": "address"
      },
      {
        "name": "_farmToken",
        "type": "address"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "snapshot",
    "inputs": [
      {
        "name": "_account",
        "type": "address"
      }
    ],
    "outputs": []
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "snapshot",
    "inputs": [
      {
        "name": "_account",
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
    "gas": 223114
  },
  {
    "stateMutability": "nonpayable",
    "type": "function",
    "name": "withdraw",
    "inputs": [
      {
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "outputs": [],
    "gas": 223121
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "lpToken",
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
    "name": "farmToken",
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
    "name": "reapIntegral",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1238
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "lastReapTimestamp",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1268
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "reapIntegralFor",
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
    "gas": 1513
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "lastReapTimestampFor",
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
    "gas": 1543
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "balances",
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
    "gas": 1573
  },
  {
    "stateMutability": "view",
    "type": "function",
    "name": "totalBalances",
    "inputs": [],
    "outputs": [
      {
        "name": "",
        "type": "uint256"
      }
    ],
    "gas": 1388
  }
]
```

## Byte code
```bin
0x604061056b61014039602061056b60c03960c05160a01c1561002057600080fd5b6020602061056b0160c03960c05160a01c1561003b57600080fd5b6000610140511415151561008e576308c379a06101805260206101a05260136101c0527f5f6c70546f6b656e206973206e6f7420736574000000000000000000000000006101e0526101c050606461019cfd5b600061016051141515156100e1576308c379a06101805260206101a05260156101c0527f5f6661726d546f6b656e206973206e6f742073657400000000000000000000006101e0526101c050606461019cfd5b610140516000556101605160015561055356600436101561000d5761032d565b600035601c52600051341561002157600080fd5b632651216081141561003857600061014052610069565b63204e94b08114156100645760243560a01c1561005457600080fd5b6020602461014037600050610069565b61009a565b60043560a01c1561007957600080fd5b61014051600435610160526101605160065801610333565b61014052600050005b63b6b55f2581141561015a5733610140526101405160065801610333565b600050600780546004358181830110156100d157600080fd5b8082019050905081555060063360e05260c052604060c02080546004358181830110156100fd57600080fd5b80820190509050815550602061020060646323b872dd61014052336101605230610180526004356101a05261015c60006000545af161013b57600080fd5b601f3d1161014857600080fd5b6000506102005161015857600080fd5b005b632e1a7d4d8114156102115733610140526101405160065801610333565b60005060063360e05260c052604060c02080546004358082101561019b57600080fd5b8082039050905081555060078054600435808210156101b957600080fd5b8082039050905081555060206101e0604463a9059cbb6101405233610160526004356101805261015c60006000545af16101f257600080fd5b601f3d116101ff57600080fd5b6000506101e05161020f57600080fd5b005b635fcbd2858114156102295760005460005260206000f35b63c2442f938114156102415760015460005260206000f35b63a006e8518114156102595760025460005260206000f35b63baf4f2cb8114156102715760035460005260206000f35b63e50da4c98114156102a75760043560a01c1561028d57600080fd5b600460043560e05260c052604060c0205460005260206000f35b63bc93934e8114156102dd5760043560a01c156102c357600080fd5b600560043560e05260c052604060c0205460005260206000f35b6327e235e38114156103135760043560a01c156102f957600080fd5b600660043560e05260c052604060c0205460005260206000f35b63a69a2ad181141561032b5760075460005260206000f35b505b60006000fd5b61016052610140526000600354111561039957600254600754426003548082101561035d57600080fd5b80820390509050808202821582848304141761037857600080fd5b8090509050905081818301101561038e57600080fd5b808201905090506002555b600060056101405160e05260c052604060c0205411156104425760046101405160e05260c052604060c0205460066101405160e05260c052604060c020544260056101405160e05260c052604060c02054808210156103f757600080fd5b80820390509050808202821582848304141761041257600080fd5b8090509050905081818301101561042857600080fd5b8082019050905060046101405160e05260c052604060c020555b426003554260056101405160e05260c052604060c0205561016051565b6100f4610553036100f46000396100f4610553036000f3
```