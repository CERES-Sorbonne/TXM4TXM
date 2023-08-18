// var Tags = ["id", "form", "lemma", "pos", "xpos", "feats", "head", "deprel", "deps", "misc", "whitespace", "text"];

function do_expand(element, target) {
    let state;
    let child;

    state = element.checked ? 'on' : 'off';

    target.setAttribute('state', state);
    target.setAttribute('aria-expanded', state === 'on' ? 'checked' : '');

    for (let i = 0; i < target.children.length; i++) {
        child = target.children[i].children[0];
        child.setAttribute('state', state);
        child.setAttribute('aria-expanded', state === 'on' ? 'checked' : '');
    }
}


function listoffiles(element) {
    for (let i = 0; i < element.files.length; i++) {
        document.getElementById('listoffiles').innerHTML += element.files[i].name + '\t';
    }
    activatesubmit();
}

function activatesubmit() {
    let ison = false;
    let reallst = document.getElementById("files");

    if (reallst.files.length > 0) {
        let lst = document.getElementsByClassName("level2checkbox");
        for (let i = 0; i < lst.length; i++) {
            if (lst[i].getAttribute('state') === 'on') {
                ison = true;
                break;
            }
        }
    }
    document.getElementById('send').disabled = !ison;
}
