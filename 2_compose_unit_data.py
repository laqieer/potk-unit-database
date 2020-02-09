# -*- coding:utf-8 -*-

import json


def parse(fn: str, key: str = 'ID') -> dict:
    with open(fn, mode='r', encoding='utf8') as fd:
        return {it[key]: it for it in json.load(fd)}


if __name__ == '__main__':
    units = parse('masterdata/UnitUnit.json')
    parameters = parse('masterdata/UnitUnitParameter.json')
    initial = parse('masterdata/UnitInitialParam.json')
    jobs = parse('masterdata/UnitJob.json')

    output = []
    for ID, it in units.items():
        print(ID)
        item = {
            'unit':       it,
            'parameters': parameters[it['parameter_data_UnitUnitParameter']],
            'initial':    initial[ID],
            'job':        jobs[it['job_UnitJob']],
        }
        output.append(item)

    with open('composed.json', mode='w', encoding='utf8') as fd:
        json.dump(output, fd, indent='\t', ensure_ascii=False)
