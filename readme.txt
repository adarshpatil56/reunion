
** users collection format:
{
    "_id" : ObjectId("633d70cdfcf7d5cb5e32a17e"),
    "user_id" : "111",
    "email" : "adarsh.p@gmail.com",
    "password" : { "$binary" : "JDJiJDEyJE5ETHpqakMuTzhUMjJlaGJvYmx6emV1cHFGZ0tjeDdVOElMaUFZWjBpcDZqMTltS1VnNGxH", "$type" : "00" },
    "role_name" : "Administrator",
    "login_source" : "portal",
    "phone_number" : "",
    "first_name" : "Adarsh",
    "last_name" : "Patil",
    "is_deleted" : false,
    "create_on" : ISODate("2022-10-05T05:45:58.720Z")
}

** users_post collection format:
{
    "_id" : ObjectId("633d8003fcf7d5cb5e32a2dc"),
    "user_id" : "111",
    "email" : "adarsh.p@gmail.com",
    "post_id" : "aaa",
    "title" : "hello universe",
    "description" : "first post",
    "is_deleted" : false,
    "create_on" : ISODate("2022-10-05T05:45:58.720Z"),
    "like_post" : [ 
        {
            "user_id" : "222",
            "like" : true,
            "comment" : null
        }
    ],
    "likes" : 1
}
