function deleteProperty(e){
    let answer = confirm('Are you sure you want to delete this property?')
    if(answer){
        const formData = new FormData();
        formData.append('card', e.target.closest('.card').id);
        fetch('/deleteproperty', {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .catch(err => console.log(err));

        e.target.closest('.card').remove();
    }
}
if (document.querySelector('.card button') !== null){
    document.querySelector('.card button').addEventListener('click', (e) => {deleteProperty(e)}, false)
}