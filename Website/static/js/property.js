const imgs = document.getElementsByClassName("carousel-item");
const imgpopup = document.querySelector('.img-popup')

for (let img of imgs) {
    img.addEventListener('click', () => {
        imgpopup.classList.add('open');
        const imgSrc = img.querySelector('.carousel-item img').getAttribute('src')
        imgpopup.querySelector('img').src = imgSrc
        if (imgpopup.querySelector('img').naturalHeight > screen.height){
            imgpopup.querySelector('img').style='height:100vh; width:auto;'
        }
        else{
            if(imgpopup.querySelector('img').naturalWidth > screen.width){
                imgpopup.querySelector('img').style='height:auto; width:100vw;'
            }
        }
    })
};

imgpopup.addEventListener('click', (e) =>{
    if(e.target.classList.contains('img-popup')){
        imgpopup.classList.remove('open')
    }
});

document.querySelector('.container').parentElement.style.overflowY='auto';