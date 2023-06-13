import { displayCity, displayState} from './layout.js'

async function getCity(){
    const res = await fetch('/filterLocation');
    let myLoc = await res.json();

    document.getElementById("formCityE").innerHTML = "<option selected>-</option>";
    
    for (let i in myLoc){
        let html = displayCity(myLoc[i]);
        document.getElementById("formCityE").appendChild(html);
    };
}
async function getState(filter){

    const res = await fetch('/filterLocation',{
        headers : {'Content-Type' : 'application/json'},
        method: 'POST',
        cache: "no-cache",
        body: JSON.stringify(filter)
    });

    let myLoc = await res.json();

    document.getElementById("formStateE").innerHTML = "<option selected>-</option>";
    
    for (let i in myLoc){
        let html = displayState(myLoc[i]);
        document.getElementById("formStateE").appendChild(html);
    };
}

async function filterProperties(){
    let city = document.getElementById("formCityE").options[document.getElementById("formCityE").selectedIndex].text;
    
    
    if(city == "-"){
        document.getElementById("formStateE").disabled = true;

    }
    else{
        document.getElementById("formStateE").disabled = false;
        let state = document.getElementById("formCityE").options[document.getElementById("formCityE").selectedIndex].text;
        getState(state);
    }


}

$(document).ready(async function() {
    
    await getCity();
           
})

document.getElementById ("formCityE").addEventListener ("change", filterProperties, false);