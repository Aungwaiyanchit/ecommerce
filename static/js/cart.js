let updateBtns = document.querySelectorAll('.updated-cart');


updateBtns.forEach((updateBtn) => {
            updateBtn.addEventListener('click', () => {
                let productId = updateBtn.dataset.product
                let action = updateBtn.dataset.action
                console.log('productId:', productId, 'action:', action);
        
                console.log('user:' , user);
               if(user == 'AnonymousUser'){
                    window.location.href = 'http://127.0.0.1:8000/login/'
               }else{   
                 updateUserOrder(productId, action)
               }
    
            })
     })
  
     const updateUserOrder = (productId, action) => {
         console.log('User is authenticated');
         let url = '/update_item/'
         fetch(url, {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
                 'X-CSRFToken': csrftoken
             },
             body: JSON.stringify( {
                 'productId': productId,
                 'action': action
             })
         })
         .then((res) => {
             return res.json()
         })
         .then((data) => {
            console.log(data);
            location.reload()
         })
     }
