import { displayCity, displayState, displayElement } from './layout.js'

var myData;

async function getData(filter){

    const res = await fetch('/get-properties', {
        headers : {'Content-Type' : 'application/json'},
        method: 'POST',
        cache: "no-cache",
        body: JSON.stringify(filter)
    });
    
    myData = await res.json();
}

async function getCity(){
    const res = await fetch('/filterLocation');
    let myLoc = await res.json();
    let counter = 1;

    document.getElementById("formCity").innerHTML = "<option selected>-</option>";
    
    for (let i in myLoc){
        let html = displayCity(myLoc[i], counter);
        document.getElementById("formCity").appendChild(html);
        counter++;
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
    let counter = 1;

    document.getElementById("formState").innerHTML = "<option selected>-</option>";
    
    for (let i in myLoc){
        let html = displayState(myLoc[i], counter);
        document.getElementById("formState").appendChild(html);
        counter++;
    };
}

async function propertiesForSale(){
    
    let filter = {'type' : 'sale'};
    await getData(filter);
    document.getElementById("propertySection").innerHTML = "";
    for (let i in myData){
        let html = displayElement(myData[i]);
        document.getElementById("propertySection").appendChild(html);
    };
}

async function propertiesForRent(){
    
    let filter = {'type' : 'rent'};
    await getData(filter);
    document.getElementById("propertySection").innerHTML = "";
    for (let i in myData){
        let html = displayElement(myData[i]);
        document.getElementById("propertySection").appendChild(html);
    };
}

async function filteredProperties(){

    var filtered

    let city = document.getElementById("formCity").options[document.getElementById("formCity").selectedIndex].text;

    if(city == "-")
    {
        if (document.getElementById('btnforsale').checked)
        {
            propertiesForSale();
        }
        else
        {
            propertiesForRent();
        }
    }
    else
    {
        let state = document.getElementById("formState").options[document.getElementById("formState").selectedIndex].text;
        
        if(state == "-")
        {
            if (document.getElementById('btnforsale').checked)
            {
                filtered = {'type': 'sale', 'city': city}
            }
            else
            {
                filtered = {'type': 'rent', 'city': city}
            }
            
        }
        else
        {
            {
                if (document.getElementById('btnforsale').checked)
                {
                    filtered = {'type': 'sale', 'city': city, 'state': state}
                }
                else
                {
                    filtered = {'type': 'rent', 'city': city, 'state': state}
                }
                
            }
        }

        await getData(filtered);
        document.getElementById("propertySection").innerHTML = "";
        for (let i in myData){
            let html = displayElement(myData[i]);
            document.getElementById("propertySection").appendChild(html);
        };
    }
}

async function filterProperties(){
    let city = document.getElementById("formCity").options[document.getElementById("formCity").selectedIndex].text;
    
    
    if(city == "-"){
        document.getElementById("formState").style.display = "none";
        document.querySelector('label[for="formState"]').style.display = 'none';

    }
    else{
        document.getElementById("formState").style.display = "flex";
        document.querySelector('label[for="formState"]').style.display = 'flex';
        let state = document.getElementById("formCity").options[document.getElementById("formCity").selectedIndex].text;
        getState(state);
    }


}

$(document).ready(async function() {
    
    if (document.getElementById('btnforsale').checked){
        
        let filterType = {'type' : 'sale'};
        await getData(filterType);
        await getCity();
        document.getElementById("propertySection").innerHTML = "";
        
        for (let i in myData){
            
            let html = displayElement(myData[i])
            document.getElementById("propertySection").appendChild(html)
        };
    }
       
})
document.getElementById ("btnforsale").addEventListener ("click", propertiesForSale, false);
document.getElementById ("btnforrent").addEventListener ("click", propertiesForRent, false);
document.getElementById ("filter_btn").addEventListener ("click", filteredProperties, false);
document.getElementById ("formCity").addEventListener ("change", filterProperties, false);