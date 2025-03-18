"""
Generated by `compile_contracts.py` script.
Compiled with Solidity v0.8.28.
"""

# source: web3/_utils/contract_sources/SimpleResolver.sol:SimpleResolver
SIMPLE_RESOLVER_BYTECODE = "0x6080604052348015600e575f5ffd5b506102758061001c5f395ff3fe608060405234801561000f575f5ffd5b5060043610610034575f3560e01c806301ffc9a7146100385780633b3b57de14610068575b5f5ffd5b610052600480360381019061004d919061012b565b610098565b60405161005f9190610170565b60405180910390f35b610082600480360381019061007d91906101bc565b6100c9565b60405161008f9190610226565b60405180910390f35b5f633b3b57de60e01b827bffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916149050919050565b5f309050919050565b5f5ffd5b5f7fffffffff0000000000000000000000000000000000000000000000000000000082169050919050565b61010a816100d6565b8114610114575f5ffd5b50565b5f8135905061012581610101565b92915050565b5f602082840312156101405761013f6100d2565b5b5f61014d84828501610117565b91505092915050565b5f8115159050919050565b61016a81610156565b82525050565b5f6020820190506101835f830184610161565b92915050565b5f819050919050565b61019b81610189565b81146101a5575f5ffd5b50565b5f813590506101b681610192565b92915050565b5f602082840312156101d1576101d06100d2565b5b5f6101de848285016101a8565b91505092915050565b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f610210826101e7565b9050919050565b61022081610206565b82525050565b5f6020820190506102395f830184610217565b9291505056fea26469706673582212208dc62afe8a6dc8c18bf574ccf1e71345567304d4e14bb992a334f1a23b49523f64736f6c634300081c0033"  # noqa: E501
SIMPLE_RESOLVER_RUNTIME = "0x608060405234801561000f575f5ffd5b5060043610610034575f3560e01c806301ffc9a7146100385780633b3b57de14610068575b5f5ffd5b610052600480360381019061004d919061012b565b610098565b60405161005f9190610170565b60405180910390f35b610082600480360381019061007d91906101bc565b6100c9565b60405161008f9190610226565b60405180910390f35b5f633b3b57de60e01b827bffffffffffffffffffffffffffffffffffffffffffffffffffffffff1916149050919050565b5f309050919050565b5f5ffd5b5f7fffffffff0000000000000000000000000000000000000000000000000000000082169050919050565b61010a816100d6565b8114610114575f5ffd5b50565b5f8135905061012581610101565b92915050565b5f602082840312156101405761013f6100d2565b5b5f61014d84828501610117565b91505092915050565b5f8115159050919050565b61016a81610156565b82525050565b5f6020820190506101835f830184610161565b92915050565b5f819050919050565b61019b81610189565b81146101a5575f5ffd5b50565b5f813590506101b681610192565b92915050565b5f602082840312156101d1576101d06100d2565b5b5f6101de848285016101a8565b91505092915050565b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f610210826101e7565b9050919050565b61022081610206565b82525050565b5f6020820190506102395f830184610217565b9291505056fea26469706673582212208dc62afe8a6dc8c18bf574ccf1e71345567304d4e14bb992a334f1a23b49523f64736f6c634300081c0033"  # noqa: E501
SIMPLE_RESOLVER_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "nodeID", "type": "bytes32"}],
        "name": "addr",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes4", "name": "interfaceID", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
SIMPLE_RESOLVER_DATA = {
    "bytecode": SIMPLE_RESOLVER_BYTECODE,
    "bytecode_runtime": SIMPLE_RESOLVER_RUNTIME,
    "abi": SIMPLE_RESOLVER_ABI,
}
