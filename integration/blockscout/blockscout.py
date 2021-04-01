#!/usr/bin/python

import argparse
import os
import re
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='BlockScout smart contract SQL generator')
    parser.add_argument('--file', dest='file', type=str,
                        help='Ganache logs', default="deploy-logs.txt")
    args = parser.parse_args()

    sql = ""
    with open(args.file, 'r') as content_file:
        content = content_file.read()

        deployed_contracts = re.findall(
            r'Nonce: ([0-9]*)[\n]*(.*)Block: ([0-9]*)(.*)[\n]*(.*) deployed at: (.*)0x([0-9,x,a-z,A-Z]*)', content)
        for contract in deployed_contracts:
            nonce = contract[0]
            block = contract[2]
            name = contract[4].replace(' ', '')
            address = contract[6]

            file_path = './build/contracts/{}.json'.format(name)

            if not os.path.exists(file_path):
                file_path = './build/interfaces/{}.json'.format(name)

            with open(file_path, 'r') as abi_content:
                abi = json.loads(abi_content.read())

                contract_name = abi['contractName']
                compiler_version = "-"
                if "compiler" in abi:
                    compiler_version = abi['compiler']['version']

                source = ""
                if "source" in abi:
                    source = abi['source'].replace(
                        '\n', '\\n').replace("'", "''")

                byte_code = abi['bytecode']

                abi_str = json.dumps(abi['abi'], separators=(',', ':'))

                sql += '''
                insert into public.addresses (fetched_coin_balance, fetched_coin_balance_block_number, hash, contract_code, inserted_at, updated_at, nonce, decompiled, verified) values
                (0,{},'''.format(block)
                sql += "E'\\\\x{}',".format(address)
                sql += "E'\\\\x{}',".format(byte_code[2:])
                sql += "now(), now(), null, false, false);\n"

                sql += '''
                insert into public.smart_contracts
                (name,compiler_version,optimization,contract_source_code,abi,address_hash,inserted_at,updated_at,constructor_arguments,optimization_runs,evm_version,external_libraries) values
                ('{}','{}',true,'{}', '{}', '''.format(contract_name, compiler_version, source, abi_str)
                sql += "E'\\\\x{}',now(),now(),null,null,null,".format(address)
                sql += "'{}');\n"

    output = open('contracts.sql', 'w')
    output.write(sql)
