#!/usr/bin/python

import argparse, re, json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BlockScout smart contract SQL generator')
    parser.add_argument('--file', dest='file', type=str, help='Ganache logs', default="deploy-logs.txt")
    args = parser.parse_args()

    sql  = ""
    with open(args.file, 'r') as content_file:
        content = content_file.read()

        deployed_contracts = re.findall( r'([a-z,A-Z,0-9]*) deployed at: (.*)0x([0-9,x,a-z,A-Z]*)', content)
        for contract in deployed_contracts:
            address = contract[2]
            name = contract[0]

            with open('./build/contracts/{}.json'.format(name), 'r') as abi_content:
                abi = json.loads(abi_content.read())

                contract_name = abi['contractName']
                compiler_version = abi['compiler']['version']
                source = abi['source'].replace('\n', '\\n')
                abi_str = json.dumps(abi['abi'], separators=(',', ':'))

                sql += '''
                insert into public.smart_contracts
                (name,compiler_version,optimization,contract_source_code,abi,address_hash,inserted_at,updated_at,constructor_arguments,optimization_runs,evm_version,external_libraries) values
                ('{}','{}',true,'{}', '{}', '''.format(contract_name, compiler_version, source, abi_str)
                sql += "E'\\\\x{}',now(),now(),null,null,null,".format(address)
                sql += "'{}');\n"

    output = open('contracts.sql', 'w')
    output.write(sql)