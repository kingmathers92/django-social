console.log('yay profile!');

const toFollowModalBody = document.getElementById('to-follow-modal-body');
const toFollowBtn = document.getElementById('to-follow-btn');
const spinnerBox = document.getElementById('spinner-box');
const modalBtn = document.getElementById('modal-btn');
const alertFade = document.getElementById('alertFade');
let toFollowLoaded = false;

console.log(toFollowModalBody);
console.log(spinnerBox);


$('#modal-btn').click(function(){
    console.log('working');
    $('.modal')
    .modal('show')
    ;
});
$('.dropdown').dropdown();


$(window).on("load",function(){
    $(".loader-wrapper").fadeOut("slow");
});


setTimeout(()=> {
    alertFade.classList.add('not-visible');
}, 2000);

let display = false;
$(".cmt_btn").click(function () {
    if (display===false) {
        $(this).next(".comment-box").show("slow");
        display=true;
    } else {
        $(this).next(".comment-box").hide("slow");
        display=false;
    }
});

$('.like-form').submit(function(e){
    e.preventDefault();
    console.log('works fine!');

    const post_id = $(this).attr('id');

    const like_text = $(`.like-btn${post_id}`).text();
    const trim = $.trim(like_text);

    const url = $(this).attr('action');

    let res;
    const likes = $(`.like-count${post_id}`).text();
    const trimCount = parseInt(likes);

    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            'post_id': post_id,

        },
        success: function(response) {
            if(trim === 'Unlike') {
                $(`.like-btn${post_id}`).text('Like');
                res = trimCount - 1;
            } else {
                $(`.like-btn${post_id}`).text('Unlike');
                res = trimCount + 1;
            }

            $(`.like-count${post_id}`).text(res);
        },
        error: function(response) {
            console.log('error', response);
        }
    });
});


// toFollowBtn.addEventListener('click', ()=>{
//     $.ajax({
//         type: 'GET',
//         url: '/profile-view/',
//         success: function(response){
//             if(!toFollowLoaded){
//                 const pfData = response.pf_data;
//             console.log(pfData);
//             setTimeout(()=> {
//                 spinnerBox.classList.add('not-visible');
//                 pfData.forEach(element => {
//                         toFollowModalBody.innerHTML += `
//                             <div class="row mb-2 align-items-center">
//                                 <div class="col-2">
//                                     <img class="avatar" src="${element.avatar}" alt="${element.user}">
//                                 </div>
//                                 <div class="col-3">
//                                     <div class="text-muted">${element.user}</div>
//                                 </div>
//                                 <div class="col text-right">
//                                     <button class="btn btn-success">Follow</button>
//                                 </div>
//                             </div>`;
//                 });
//             }, 2000);
//             }
//             toFollowLoaded = true;
//         },
//         error: function(error){
//             console.log(error);
//         }
//     });
// });

