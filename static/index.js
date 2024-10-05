import { createClient } from "@propelauth/javascript";

const authClient = createClient({
    // The base URL where your authentication pages are hosted. You can find this under the Frontend Integration section for your project.
    authUrl: "https://62994739.propelauthtest.com",
    // If true, periodically refresh the access token in the background. This helps ensure you always have a valid token ready to go. Default true.
    enableBackgroundTokenRefresh: true,
});

console.log("Auth client initialized:", authClient);

(async () => {
    const authInfo = await authClient.getAuthenticationInfoOrNull();
    if (authInfo) {
        console.log("User is logged in as", authInfo.user.email);
    } else {
        console.log("User is not logged in");
    }

    // Hook up buttons to redirect to signup, login, etc
    document.getElementById("signup").onclick = authClient.redirectToSignupPage;
    document.getElementById("login").onclick = authClient.redirectToLoginPage;
    document.getElementById("account").onclick = authClient.redirectToAccountPage;
    document.getElementById("logout").onclick = authClient.logout;

    // When the logged in status changes, display one of the divs
    authClient.addLoggedInChangeObserver((isLoggedIn) => {
        if (isLoggedIn) {
            document.getElementById("display-when-logged-in").style.display = "revert";
            document.getElementById("display-when-logged-out").style.display = "none";

            // Get authentication info and set email to it
            authClient.getAuthenticationInfoOrNull()
                .then(authInfo => {
                    document.getElementById("email").innerText = authInfo?.user?.email;
                });
        } else {
            document.getElementById("display-when-logged-in").style.display = "none";
            document.getElementById("display-when-logged-out").style.display = "revert";
        }
    });
})();