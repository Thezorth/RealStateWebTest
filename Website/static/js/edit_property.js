const btns = document.querySelectorAll('.carousel-item button')
const textedit = document.querySelectorAll('h1, h4, h5')
const submit_btn = document.getElementById('btn_smit')
var jsonfile = {'id':propertyid, 'saletype': saletype, 'value': value, 'address': address }
var delete_image = []
const formData = new FormData();

function submit_data(){    
    if(formData.has('usertext')){
        formData.delete('usertext')
    }
    formData.append('usertext', JSON.stringify(jsonfile))
    formData.append('delete', JSON.stringify(delete_image))

    console.log(formData)

    fetch('/editproperty', {
        method: 'POST',
        body: formData,
    })
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.log(err));

}

for (let txt of textedit){
    txt.addEventListener('click', (e) =>{
        switch (e.target.id){
            case 'propsaletype':
                if(e.target.innerHTML == 'For Sale'){
                    jsonfile.saletype = 'rent';
                    e.target.innerHTML = 'For Rent';
                }
                else{
                    jsonfile.saletype = 'sale';
                    e.target.innerHTML = 'For Sale';
                }
                break;
            case 'proplocation':
                let loc = prompt('Insert new address');
                if(loc != "" & loc != null){
                    jsonfile.address = loc;
                    e.target.innerHTML = 'Location: '+loc;
                }
                break;
            case 'propprice':
                let price = prompt('Insert new value');
                if(price != "" & price != null & /^[0-9]+$/.test(price)){
                    jsonfile.value = price;
                    e.target.innerHTML = 'Price: '+price+" $";
                }
                break;
}})}

for (let btn of btns) {
    btn.addEventListener('click', (e) => {
        let text = e.target.innerHTML;
        if (text == 'Edit'){
            let input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/png, image/jpg, image/jpeg'
            
            input.onchange = (e) => { 
                let file = e.target.files[0];
                let reader = new FileReader();
                if(formData.has(document.querySelector('.carousel-item.active img').id)){
                    formData.delete(document.querySelector('.carousel-item.active img').id)
                }
                formData.append(document.querySelector('.carousel-item.active img').id, file)
                console.log(formData)
                reader.readAsDataURL(file);
                
                reader.onload = (readerEvent) => {
                    let content = readerEvent.target.result;
                    let img = document.querySelector('.carousel-item.active img')
                    img.src=content;
                    img.alt=content;

                 }
             }

            input.click();

        }
        else{
            let answer = confirm('You are about to delete this image!')
            if (answer) {
                if(formData.has(document.querySelector('.carousel-item.active img').id)){
                    formData.delete(document.querySelector('.carousel-item.active img').id)
                }
                delete_image.push(document.querySelector('.carousel-item.active img').id)
                document.querySelector('.carousel-item.active').remove()
                let nodelist = document.querySelectorAll('.carousel-item');
                if (Object.keys(nodelist).length > 0){
                    document.querySelector('.carousel-item').classList.add('active');
                }                
        }};
    });
};

submit_btn.addEventListener('click', submit_data, false)
document.querySelector('.container').parentElement.style.overflowY='auto';