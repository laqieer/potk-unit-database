# -*- coding:utf-8 -*-

import json


def main():
    units = {
        it['ID']: it for it in load('masterdata/UnitUnit.json')
    }
    parameters = {
        it['ID']: it for it in load('masterdata/UnitUnitParameter.json')
    }
    initial = {
        it['ID']: it for it in load('masterdata/UnitInitialParam.json')
    }
    jobs = {
        it['ID']: it for it in load('masterdata/UnitJob.json')
    }
    # TODO Fix when my brain starts working again
    types = {}
    for it in load('masterdata/UnitTypeParameter.json'):
        key = it['rarity_UnitRarity']
        if key not in types:
            types[key] = []
        types[key].append(it)

    output = []
    for ID, it in units.items():
        print(ID)
        item = {
            'unit':       it,
            'parameters': parameters[it['parameter_data_UnitUnitParameter']],
            'initial':    initial[ID],
            'job':        jobs[it['job_UnitJob']],
            'types':      types[it['rarity_UnitRarity']]
        }
        output.append(item)

    with open('composed.json', mode='w', encoding='utf8') as fd:
        json.dump(output, fd, indent='\t', ensure_ascii=False)


def load(fn: str) -> list:
    with open(fn, mode='r', encoding='utf8') as fd:
        return json.load(fd)


if __name__ == '__main__':
    main()
