import argparse
import json
import os
import subprocess
import sys

from glob import glob

ZERO = '00' * 32

def main():
    parser = argparse.ArgumentParser(description='EVM assembly runner.')
    parser.add_argument('source', metavar='source', type=str, help='entry file for assembling')

    args = parser.parse_args()

    if len(sys.argv) != 2:
        print("invalid number of arguments")
        sys.exit(1)

    asm = assemble_program(args.source)
    env = get_t8n_input(asm)
    run_t8n(env)
    run_traceview()


def assemble_program(source):
    out = subprocess.run(["eas", source], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if out.returncode != 0:
        print(f"Failed to assemble {source}:\n")
        print(out.stderr.decode('ascii'))
        sys.exit(1)

    return out.stdout.decode('ascii').rstrip()


def get_t8n_input(asm):
    with open('debug/env.json') as f:
      data = json.load(f)

    data['alloc']['0x095e7baea6a6c7c4c2dfeb977efac326af552d87']['code'] = f"0x{asm}"
    data['txs'][0]['input'] = f"0x{build_input()}"

    print(data)

    return data


def run_t8n(env):
    args = ["evm", "t8n", "--input.alloc=stdin", "--input.env=stdin", "--input.txs=stdin", "--output.result=stdout", "--output.alloc=stdout", "--trace"]
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)
    proc.communicate(str.encode(json.dumps(env)))

    if proc.returncode != 0:
        print(f"Failed to execute t8n\n")
        print(out.stderr.decode('ascii'))
        sys.exit(1)


def run_traceview():
    trace = glob("*.jsonl")[0]
    subprocess.run(["traceview", trace])
    os.remove(trace)

def build_input():
    data = {
        'selector': ZERO,
        'parent_hash': fill32('01'),
        'coinbase': fill32('02'),
        'state_root': fill32('03'),
        'receipt_root': fill32('04'),
        'bloom': fill32('05'),
        'number': fill32('06'),
        'gas_used': fill32('07'),
        'time': fill32('08'),
        'base_fee': fill32('09'),
        'tx_type': fill32('10'),
        'chain_id': fill32('11'),
        'nonce': fill32('12'),
        'gas_tip_cap': fill32('13'),
        'gas_fee_cap': fill32('14'),
        'gas_limit': fill32('15'),
        'to': fill32('16'),
        'value': fill32('17'),
        'y_parity': fill32('18'),
        'r': fill32('19'),
        's': fill32('20'),
        'data_len': ZERO,
        'proof_len': pad32('05'),
        'data': '',
        'proof': '6001600201',
    }

    out = ''
    for (k, v) in data.items():
        out += v

    return out


def pad32(val):
    return val.zfill(64)

def fill32(val):
    return val*32

    return val.zfill(64)

if __name__=="__main__":
    main()
