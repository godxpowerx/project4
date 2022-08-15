document.addEventListener('DOMContentLoaded', function () {
    try {
        // Use buttons to toggle between views
        document.querySelector('#addpost').addEventListener('click', add_post);
        document.querySelector('#view_post').addEventListener('click', show_post);
        document.querySelector('#my_profile').addEventListener('click', profile_page);
        document.querySelector('#following').addEventListener('click', following_post);
        //document.querySelector('#following').addEventListener('click', view);

        // send a mail
        document.querySelector('#add-post-form').addEventListener('submit', submit_post);
        document.querySelector('#edit-post-form').addEventListener('submit', submit_edit_post);

        show_post();
    }
    catch {
        document.getElementById("error-form").className = 'bg-danger text-center'
        document.getElementById("error-form").innerHTML = 'Sign-in to add post, comment and like'
    }

});


function submit_post(event) {
    event.preventDefault()

    post_body = document.querySelector('#post-body').value;

    // make sure the user is not trying to send an empty email
    if (post_body === '') {
        document.querySelector('#error-form').innerHTML = 'the body or subject can\'t be empty';
        return
    }

    // if the value are correct its is sent to the server for more proccessing and depending
    // on the response will determine what  the user will see
    fetch('/create_post', {
        method: 'POST',
        body: JSON.stringify({
            body: post_body
        })
    })
        .then(response => response.json())
        .then(result => {
            // if the response from the server is success the user will see a message 
            // else and error will be displayed

            show_post();

            if (result.message) {
                document.querySelector('#error-form').className = 'bg-success'
                document.querySelector('#error-form').innerHTML = result.message
            } else {
                document.querySelector('#error-form').className = 'bg-danger'
                document.querySelector('#error-form').innerHTML = result.error
            }

        });

}

function following_post() {
    document.querySelector('#add_post').style.display = 'none';
    document.querySelector('#edit_post').style.display = 'none';

    document.querySelector('#post_content').innerHTML = "";
    document.querySelector('#post_content').style.display = 'none';

    document.querySelector('#profile_page').style.display = 'none';
    document.querySelector('#following-post-content').style.display = 'block';
    document.querySelector('#view_profile').style.display = 'none';

    document.querySelector('#following-post-content').innerHTML = "";

    let rpage = 1;
    try {
        if (this.dataset.page_num !== undefined) {
            rpage = this.dataset.page_num;
        }
    } catch {
        rpage = 1;
    }

    fetch(`/following_post/${rpage}`)
        .then(response => response.json())
        .then(result => {

            let data = result.total

            for (da in data) {
                let contain = fill_posts(data[da]);

                document.getElementById("following-post-content").insertAdjacentHTML("beforeend",
                    contain);
                document.getElementById(`${data[da].id}viewcomment`).addEventListener('click', show_comment)
                document.getElementById(`${data[da].id}comment-form`).addEventListener("submit", submit_comment);

            }

            let page_scroll = '<div class="text-center">';
            if (result.prev) {
                page_scroll += `<button id="prev-page" data-page_num=${result.page_num - 1} class="bg-info col-3"> Previous </button>`
            }
            if (result.next) {
                page_scroll += `<button id="next-page" data-page_num=${result.page_num + 1} class="bg-info col-3"> Next </button>`
            }
            page_scroll += '</div>'

            document.getElementById("following-post-content").insertAdjacentHTML("beforeend",
                page_scroll);

            document.getElementById("following-post-content").insertAdjacentHTML("beforeend",
                `<p class="text-center text-white">current page
                 ${result.page_num}</p>`);

            if (result.prev) {
                document.getElementById('prev-page').addEventListener('click', following_post)
            }
            if (result.next) {
                document.getElementById('next-page').addEventListener('click', following_post)
            }

            const profile_detail = document.querySelectorAll('.profile_id');
            profile_detail.forEach(element => {
                element.addEventListener('click', view_profile)
            });

            const liking_post = document.querySelectorAll('.liked');
            liking_post.forEach(element => {
                element.addEventListener('click', liked_post)
            })



        });


}

function add_post() {
    // Show the mailbox and hide other views
    document.querySelector('#add_post').style.display = 'block';
    document.querySelector('#edit_post').style.display = 'none';

    document.querySelector('#post_content').style.display = 'none';
    document.querySelector('#profile_page').style.display = 'none';
    document.querySelector('#following-post-content').style.display = 'none';
    document.querySelector('#view_profile').style.display = 'none';

    document.querySelector('#post-body').value = '';

}

function fill_posts(data) {
    let contain = `
                <div class="main-con container border col-10 bg-info col-md-7 mt-4">
                    <h5 class="">
                        <a id="${data.user_id}" class="text-decoration-none text-dark profile_id" href="#">
                            ${data.user}
                        </a> `
    if (data.original_users) {
        contain += `<a id="${data.id}edit" class="edit" data-edit_id="${data.id}">
                    Edit</a>`
    }
    contain += `
                   </h5>
                    <div>
                        <div class="d-flex justify-content-center bg-white">
                            <h1>
                                <blockquote class="m-2 p-2">${data.post_content}</blockquote>
                            </h1>
                        </div>
                        
                        <div id="${data.id}change_heart">
                            `
    if (data.liked) {
        contain += `<a  id="${data.id}heart" data-like_id="${data.id}" data-liked_type="unliked" 
                    class='text-danger lead text-decoration-none liked liked_heart'> &hearts; </a>
                    </div>`
    } else {
        contain += `<a id="${data.id}heart" data-like_id="${data.id}" data-liked_type="likings"
                     class='text-white lead text-decoration-none liked liked_heart'> &hearts; </a></div>`
    }

    contain += `<h6> <span id="${data.id}like" class="like_no">${data.no_likes}</span> likes</h6>
           
            <div>
                    <p> <span id="${data.id}nocomment" class="no_comment">${data.no_comment}</span> comment</p>    

            <form id="${data.id}comment-form" data-comment_id="${data.id}">
            <div class="form-group">
                <textarea id="${data.id}comment" class=" commenttext form-control" placeholder="add your comment"></textarea>
                <input type="submit" class="btn btn-primary   col-3"/>
            </div>
        </form>
        <a class="text-center" id="${data.id}viewcomment" data-comment_id="${data.id}">show comment</a>
        <div id="${data.id}showcomment" ></div>

        </div>
                    </div>

                </div>`;
    
    return contain
}

function show_post() {
    document.querySelector('#add_post').style.display = 'none';
    document.querySelector('#edit_post').style.display = 'none';

    document.querySelector('#post_content').style.display = 'block';
    document.querySelector('#profile_page').style.display = 'none';


    document.querySelector('#following-post-content').innerHTML = "";
    document.querySelector('#following-post-content').style.display = 'none';

    document.querySelector('#view_profile').style.display = 'none';


    document.querySelector('#post_content').innerHTML = "";
    let rpage = 1;
    try {
        if (this.dataset.page_num !== undefined) {
            rpage = this.dataset.page_num;
        }
    } catch {
        rpage = 1;
    }

    fetch(`/all_post/${rpage}`)
        .then(response => response.json())
        .then(result => {
            const data = result.total
            for (da in data) {
              

                let contain = fill_posts(data[da]);

                document.getElementById("post_content").insertAdjacentHTML("beforeend",
                    contain);

                document.getElementById(`${data[da].id}viewcomment`).addEventListener('click', show_comment);

                if (data[da].original_users) {
                    document.getElementById(`${data[da].id}edit`).addEventListener('click', edit_post)
                }
                document.getElementById(`${data[da].id}comment-form`).addEventListener("submit", submit_comment);
            }
            let page_scroll = '<div class="text-center">';
            if (result.prev) {
                page_scroll += `<button id="prev-page" data-page_num=${result.page_num - 1} class="bg-info col-3"> Previous </button>`
            }
            if (result.next) {
                page_scroll += `<button id="next-page" data-page_num=${result.page_num + 1} class="bg-info col-3"> Next </button>`
            }
            page_scroll += '</div>'

            document.getElementById("post_content").insertAdjacentHTML("beforeend",
                page_scroll);

            document.getElementById("post_content").insertAdjacentHTML("beforeend",
                `<p class="text-center text-white">total page ${result.total_page}-- current page
                 ${result.page_num}</p>`);

            if (result.prev) {
                document.getElementById('prev-page').addEventListener('click', show_post)
            }
            if (result.next) {
                document.getElementById('next-page').addEventListener('click', show_post)
            }


            const profile_detail = document.querySelectorAll('.profile_id');
            profile_detail.forEach(element => {
                element.addEventListener('click', view_profile)
            });

            const liking_post = document.querySelectorAll('.liked');
            liking_post.forEach(element => {
                element.addEventListener('click', liked_post)
            })
        });
}

function profile_page() {
    document.querySelector('#add_post').style.display = 'none';
    document.querySelector('#edit_post').style.display = 'none';

    document.querySelector('#post_content').style.display = 'none';
    document.querySelector('#profile_page').style.display = 'block';
    document.querySelector('#following-post-content').style.display = 'none';
    document.querySelector('#view_profile').style.display = 'none';

    document.getElementById("og-user-posts").innerHTML = '';

    fetch('user_posts')
        .then(response => response.json())
        .then(postes => {

            
            for (da in postes) {
                let contain = fill_posts(postes[da]);

                document.getElementById("og-user-posts").insertAdjacentHTML("beforeend",
                    contain);

                document.getElementById(`${postes[da].id}viewcomment`).addEventListener('click', show_comment);

                document.getElementById(`${postes[da].id}comment-form`).addEventListener("submit", submit_comment);
            }

            const liking_post = document.querySelectorAll('.liked');
            liking_post.forEach(element => {
                element.addEventListener('click', liked_post)
            })

            const profile_detail = document.querySelectorAll('.profile_id');
            profile_detail.forEach(element => {
                element.addEventListener('click', view_profile)
            });
            const follow_button = document.querySelectorAll('.follow_id');
            follow_button.forEach(element => {
                element.addEventListener('click', follow_switch)
            });

        });

}

function view_profile() {
    document.querySelector('#add_post').style.display = 'none';
    document.querySelector('#edit_post').style.display = 'none';

    document.querySelector('#post_content').style.display = 'none';
    document.querySelector('#profile_page').style.display = 'none';
    document.querySelector('#following-post-content').style.display = 'none';
    document.querySelector('#view_profile').style.display = 'block';

    profile_with_id(this.id)

}

function profile_with_id(id) {
    fetch(`/profile_page/${id}`)
        .then(response => response.json())
        .then(data => {
            if (data.original_user) {
                return profile_page()
            }

            //convert the first letter to uppercase and then display it
            username = data.user.username
            document.getElementById('profile_username').innerHTML = username.charAt(0).toUpperCase() + username.slice(1);

            document.getElementById('profile_email').innerHTML = data.user.email

            document.getElementById('profile_joined').innerHTML = data.user.date_joined

            document.getElementById('last_seen').innerHTML = data.user.last_login

            document.getElementById('total_post').innerHTML = data.posts.length

            document.getElementById('no_follower').innerHTML = data.follower.length

            document.getElementById('no_following').innerHTML = data.following.length

            document.getElementById('profile_follower').innerHTML = '';
            document.getElementById('profile_following').innerHTML = '';
            document.getElementById("user-posts").innerHTML = '';


            if (data.following_user) {
                const followType = document.querySelector('.follow_id');
                followType.id = data.user.id;
                followType.innerHTML = 'Unfollow';

            } else {
                const followType = document.querySelector('.follow_id');
                followType.id = data.user.id;
                followType.innerHTML = 'Follow';

            }

            for (n in data.following) {

                document.getElementById('profile_following').innerHTML += `
            <li><a id="${data.following[n].following_id}" class="text-decoration-none text-white profile_id" href="#">
                ${data.following[n].following}</a></li>`

            }

            for (n in data.follower) {

                document.getElementById('profile_follower').innerHTML += `
            <li><a id="${data.follower[n].user_id}" class="text-decoration-none text-white profile_id" href="#">
                ${data.follower[n].user}</a></li>`

            }
            const postes = data.posts;
            for (da in postes) {
                let contain = fill_posts(postes[da]);

                document.getElementById("user-posts").insertAdjacentHTML("beforeend",
                    contain);

                document.getElementById(`${postes[da].id}viewcomment`).addEventListener('click', show_comment);

                document.getElementById(`${postes[da].id}comment-form`).addEventListener("submit", submit_comment);
            }

            const liking_post = document.querySelectorAll('.liked');
            liking_post.forEach(element => {
                element.addEventListener('click', liked_post)
            })

            const profile_detail = document.querySelectorAll('.profile_id');
            profile_detail.forEach(element => {
                element.addEventListener('click', view_profile)
            });
            const follow_button = document.querySelectorAll('.follow_id');
            follow_button.forEach(element => {
                element.addEventListener('click', follow_switch)
            });


        });

}

function follow_switch() {

    options = this.innerHTML.toUpperCase();
    ids = this.id;
    fetch(`follow_switch/${ids}`, {
        method: 'PUT',
        body: JSON.stringify({
            follow: options
        })
    })
        .then(response => response.json())
        .then(result => {

            profile_with_id(this.id)

        });
}

function liked_post() {
    const id = this.dataset.like_id

    if (this.dataset.liked_type === 'likings') {

        fetch(`liking/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                liked: true
            })
        })
            .then(response => response.json())
            .then(data => {
                let heart = `<a id="${id}heart" data-like_id="${id}" data-liked_type="unliked"
                        class='text-decoration-none liked liked_heart text-danger lead'>
                        &hearts;
                    </a>
                    `
                document.getElementById(`${id}change_heart`).innerHTML = heart;

                document.getElementById(`${id}like`).innerHTML = data['no_likes'];


                document.getElementById(`${id}heart`).addEventListener('click', liked_post)
            });

    } else if (this.dataset.liked_type === 'unliked') {

        fetch(`liking/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                liked: false
            })
        })
            .then(response => response.json())
            .then(data => {

                let heart = `<a id="${id}heart" data-like_id="${id}" data-liked_type="likings"
                        class='text-decoration-none liked liked_heart text-white lead'>
                        &hearts;
                    </a>
                    `

                document.getElementById(`${id}change_heart`).innerHTML = heart

                document.getElementById(`${id}like`).innerHTML = data['no_likes'];

                document.getElementById(`${id}heart`).addEventListener('click', liked_post)

            });
    }


}

function submit_comment(event) {
    event.preventDefault()

    const post_comment_id = this.dataset.comment_id
    const post_comment = document.getElementById(`${post_comment_id}comment`).value.trim()

    console.log(post_comment_id)
    console.log(post_comment)
    if (post_comment === "" && post_comment === " ") {
        alert('comment cant be empty')
        return false;
    }

    fetch(`post_comment/${post_comment_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            post_com: post_comment
        })
    })
        .then(response => response.json())
        .then(data => {

            if (data.error) {
                document.getElementById(`${post_comment_id}comment`).placeholder = "comment cant be empty"
                return;
            }
            document.getElementById(`${post_comment_id}comment`).value = ""
            document.getElementById(`${post_comment_id}nocomment`).innerHTML = data.no_comment
        })
}

function show_comment() {

    const comment_id = this.dataset.comment_id

    if (this.innerHTML.trim() === "show comment") {

        document.getElementById(`${comment_id}showcomment`).style.display = 'block'
        document.getElementById(`${comment_id}showcomment`).innerHTML = ''

        fetch(`view_comment/${comment_id}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    this.innerHTML = "hide comment"
                    document.getElementById(`${comment_id}showcomment`).insertAdjacentHTML("beforeend",
                        "no comment");
                    return;
                } else {
                    for (d in data) {
                        user_name = `<div>
                <span class="lead bg-grey text-white">
                ${data[d].user}
                </span><span class="lead">
                ${data[d].comment}</span>
                </div>`
                        this.innerHTML = "hide comment"
                        document.getElementById(`${comment_id}showcomment`).insertAdjacentHTML("beforeend",
                            user_name);
                    }
                }
            })
    } else {
        this.innerHTML = 'show comment'
        document.getElementById(`${comment_id}showcomment`).style.display = 'none'
    }
}

function edit_post() {

    document.querySelector('#add_post').style.display = 'none';
    document.querySelector('#edit_post').style.display = 'block';

    document.querySelector('#post_content').style.display = 'none';
    document.querySelector('#profile_page').style.display = 'none';
    document.querySelector('#following-post-content').style.display = 'none';
    document.querySelector('#view_profile').style.display = 'none';

    document.querySelector('#edit-post-body').value = '';

    const post_id = this.dataset.edit_id

    fetch(`edit_post/${post_id}`)
        .then(response => response.json())
        .then(data => {
            contain = `<input disabled value="${post_id}" id="edited-post-id" type="hidden" >`
            document.getElementById("edit-post-id").innerHTML = contain;
            document.querySelector('#edit-post-body').value = data.post_content;
        })
}

function submit_edit_post(event) {
    event.preventDefault()

    post_body = document.querySelector('#edit-post-body').value;
    id = document.querySelector('#edited-post-id').value;
    // make sure the user is not trying to send an empty email
    if (post_body === '') {
        document.querySelector('#error-form').innerHTML = 'the body can\'t be empty';
        return
    }

    // if the value are correct its is sent to the server for more proccessing and depending
    // on the response will determine what  the user will see
    fetch(`edit_post/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            body: post_body
        })
    })
        .then(response => response.json())
        .then(result => {
            // if the response from the server is success the user will see a message 
            // else and error will be displayed

            show_post();

            if (result.message) {
                document.querySelector('#error-form').className = 'bg-success'
                document.querySelector('#error-form').innerHTML = result.message
            } else {
                document.querySelector('#error-form').className = 'bg-danger'
                document.querySelector('#error-form').innerHTML = result.error
            }

        });
}
