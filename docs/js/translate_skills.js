'use strict';

class Skill {
    constructor(skillId) {
        this.iid = skillId;
        this.lang = "jp";
        this._nameElement = null;
        this._descElement = null;
        this.jp = {};
        this.en = null;
    }

    load(element) {
        var field = '' + element.dataset.skillField;
        this[`_${field}Element`] = element;
        this.jp[field] = element.textContent.toString().trim();
    }

    fetchEn() {
        return fetch(`/data/translations/en/skill/${this.iid}.json`).then(
            r => r.json()
        ).then(
            d => this.en = d
        );
    }

    setLang(lang) {
        const info = this[lang];
        if (!info)
            return;
        this._nameElement.textContent = info.name;
        this._descElement.textContent = info.desc;
    }

    toString() {
        return `Skill(${this.iid}, jp:${!!this.jp}, en:${!!this.en})`;
    }
}

var skills = [];

function getOrCreate(map, skillId) {
    var entry = map.get(skillId);
    if (!entry) {
        entry = new Skill(skillId);
        map.set(skillId, entry);
    }
    return entry;
}

function setup() {
    const toggle = document.getElementById("toggle-lang");
    const setJp = document.getElementById("lang-jp");
    const setEn = document.getElementById("lang-en");

    setJp.addEventListener('click', ev => skills.forEach(s => s.setLang("jp")));
    setEn.addEventListener('click', ev => skills.forEach(s => s.setLang("en")));

    var pageSkills = new Map();

    for (const element of document.querySelectorAll('[data-skill-id]')) {
        var skill = getOrCreate(pageSkills, element.dataset.skillId);
        skill.load(element);
    }

    skills = [ ...pageSkills.values() ];
    Promise.allSettled(
        skills.map(s => s.fetchEn())
    ).then(_ => {
        const allFailed = !skills.some(s => s.en);
        setEn.disabled = allFailed;
        toggle.hidden = allFailed;
    });
}

setup();
