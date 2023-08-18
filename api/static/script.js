// var Tags = ["id", "form", "lemma", "pos", "xpos", "feats", "head", "deprel", "deps", "misc", "whitespace", "text"];

function do_expand(element, target) {
    let state;
    let child;

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
    activatesubmit();
}


function listoffiles(element) {
    for (let i = 0; i < element.files.length; i++) {
        document.getElementById('listoffiles').innerHTML += element.files[i].name + '\t';
    }
    activatesubmit();
}

function activatesubmit() {
    let ison = false;
    let lst = document.getElementsByClassName("level2checkbox");
    let reallst = document.getElementById("files");

    for (let i = 0; i < lst.length; i++) {
        if (lst[i].getAttribute('state') === 'on') {
            ison = true;
            break;
        }
    }

    if (reallst.files.length < 0) {
        ison = false;
    }

    if (ison) {
        document.getElementById('send').disabled = false;
        console.log(document.getElementById('send'));
        console.log(document.getElementById('send').disabled);
    } else {
        document.getElementById('send').disabled = true;

    }
}


