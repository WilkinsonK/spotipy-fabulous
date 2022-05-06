from spotipy.oauth.auth import ClientCredentialsFlow, AuthorizationFlow


if __name__ == "__main__":
    client_id     = "a36aaf99dad34fe294d46d284664e5ba"
    client_secret = "94944c3bc2534c7f9fe576ddbc6d6af9"

    redirect_url = "http://127.0.0.1:9090"

    auth_flow = AuthorizationFlow(
        client_id=client_id,
        client_secret=client_secret,
        redirect_url=redirect_url,
        scope=["user-follow-read"])

    print(auth_flow.get_access_token())
