console.log("running the js!");
const urlParams = new URLSearchParams(window.location.search);
const redirect_url = urlParams.get('u');
const discord_id = urlParams.get('a');
const guild_id = urlParams.get('b');


document.cookie = "discord_id="+discord_id;
document.cookie = "guild_id="+guild_id;


console.log(redirect_url);
window.location.href = redirect_url;



