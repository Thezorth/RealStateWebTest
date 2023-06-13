

function displayElement(data){
    let template = document.createElement("template");
    template.innerHTML = `<div class="card mt-5 mx-2 border-0 text-white ms-5 me-5" style="width: 18rem; height: fit-content; min-width: 18rem; min-height: fit-content; background-color: rgb(95, 64, 23);"><img src="${data.thumbnail}" class="card-img-top" style="height: auto; width: auto;" alt="..."></img><div class="card-body text-center container p-2" tyle="height: auto; min-width: auto;"><h4 class="card-title m-0">$${data.value}</h4><p class="card-text mb-0">${data.address}</p><a href="/property/${data.id}" class="btn btn-primary m-1 pt-0 pb-0 ps-4 pe-4">View</a></div></div>`;

    return template.content.firstElementChild;
}

function displayCity(data){
      
    let template = document.createElement("template");
    template.innerHTML += `<option value="${data.city}">${data.city}</option>`;

    return template.content.firstElementChild;
}

function displayState(data){
      
    let template = document.createElement("template");
    template.innerHTML += `<option value="${data.state}">${data.state}</option>`;

    return template.content.firstElementChild;
}

export { displayCity, displayElement, displayState };