var Tags = ["id", "form", "lemma", "pos", "xpos", "feats", "head", "deprel", "deps", "misc", "whitespace", "text"];

function do_expand(element, target) {
    let state; let child;

    state = element.checked ? 'on' : 'off';

    target.setAttribute('state', state);

    if (state === 'on') {
        target.removeAttribute('aria-expanded');
    } else {
        target.setAttribute('aria-expanded', 'false');
    }

    for (let i = 0; i < target.children.length; i++) {
        child = target.children[i].children[0];
        child.setAttribute('state', state);

        if (state === 'on') {
            child.removeAttribute('aria-expanded');
        } else {
            child.setAttribute('aria-expanded', 'false');
        }
    }
}


function listoffiles(element) {
    for (let i = 0; i < element.files.length; i++) {
        document.getElementById('listoffiles').innerHTML += element.files[i].name + '\t';
    }
}
