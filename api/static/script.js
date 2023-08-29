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
    let reallst = document.getElementById("files");

    if (reallst.files.length > 0) {
        // console.log(reallst.files.length);
        let lst = document.getElementsByClassName("activateSubmit");
        for (let i = 0; i < lst.length; i++) {
            if (lst[i].getAttribute('state') === 'on') {
                // console.log(lst[i].getAttribute('state'));
                ison = true;
                break;
            }
        }
    }
    // console.log(ison);
    document.getElementById('send').disabled = !ison;
}
