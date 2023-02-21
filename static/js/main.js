$(document).ready(
    function(){
        let url = 'http://127.0.0.1:8000/'
        $('.upvoteq').click(async function(){
            var sendurl = url + 'upvote-question/'
            var response = await senddata(sendurl,$(this).data('question'))
            location.reload()
        })
        $('.downvoteq').click(async function(){
            var sendurl = url + 'downvote-question/'
            var response = await senddata(sendurl,$(this).data('question'))
            location.reload()
        })
        $('.upvote-answer').click(async function(){
            var sendurl = url + 'upvote-answer/'
            var response = await senddata(sendurl,$(this).data('answer'))
            location.reload()
        })
        $('.downvote-answer').click(async function(){
            var sendurl = url + 'downvote-answer/'
            var response = await senddata(sendurl,$(this).data('answer'))
            location.reload()
        })
        $('.delete-popup').on('show',function(e){
            var button = $(e.relatedTarget);
            var data = button.data('post');
            var modal = $(this)
            modal.find('.model-dialog .model-content .model-header .modal-title').text(121212)
            modal.find('input').val('data')
        })
    }
)

async function senddata(url, data){
    const resp = await fetch(url,{
        method:'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'content' : data
        })
    })
    return resp
}