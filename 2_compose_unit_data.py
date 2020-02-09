# -*- coding:utf-8 -*-

import json

if __name__ == '__main__':
    with open('masterdata/UnitUnit.json', mode='r', encoding='utf8') as fd:
        units = {it['ID']: it for it in json.load(fd)}
    with open('masterdata/UnitUnitParameter.json', mode='r', encoding='utf8' ) as fd:
        parameters = {it['ID']: it for it in json.load(fd)}
    with open('masterdata/UnitInitialParam.json', mode='r', encoding='utf8') as fd:
        initial = {it['ID']: it for it in json.load(fd)}

    output = []
    for ID, unit in units.items():
        print(ID)
        item = {
            'Unit': unit,
            'Parameters': parameters[ID],
            'Initial': initial[ID],
        }
        output.append(item)

    with open('composed.json', mode='w', encoding='utf8') as fd:
        json.dump(output, fd, indent='\t')
