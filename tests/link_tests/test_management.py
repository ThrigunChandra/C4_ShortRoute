from tests.create_account import create_account

# Testing creating two links with same user and list them 

def test_listing_links(client):
    # Created a account
    register, login = create_account(client)

    # create links
    links = [f"https://www.example.com/{i}" for i in range(5)]

    for i in range(5):
        client.post(
            "/api/links",
            json = {
                "given_url": str(links[i])
                }
        )

    # generate all links I mean get them all and see whether they match or not 

    response = client.get(
        "/api/links"
    )

    assert response.status_code == 200, response.text 
    body = response.json()

    print(body)
    # [0]{"id" : 4}

    for i in range(5):
        # We get those in descending order
        assert body[i]["destination_url"] == links[5 - i - 1]

def test_details_of_link(client):
    # Create a Account
    create_account(client)

    # create a link
    response = client.post(
        "/api/links",
        json = {
            "given_url" : "https://www.instagram.com"
            }
    )
    assert response.status_code == 201, response.text 
    short_code = response.json()["short_code"]

    # Fetching Link by Id 
    links = client.get("/api/links")
    links = links.json()

    assert links

    link = next(item for item in links if item["short_code"] == short_code)
    link_id = link["id"] 

    assert isinstance(link_id, int)

    detail_response = client.get(
        f"/api/links/{link_id}"
    )
    assert detail_response.status_code == 200, detail_response.text 
    body = detail_response.json() 
    assert body["Click Count"] == 0
    assert body["Link"] == "https://www.instagram.com/"


# Need to verify this test_case again 
# Created by chat gpt 
# I'm just drained.. 🫠

def test_delete_link(client):
    # Register and log in
    create_account(client)

    created = client.post(
        "/api/links",
        json={"given_url": "https://www.instagram.com"}
    )
    assert created.status_code == 201, created.text
    short_code = created.json()["short_code"]

    # Find the created link's ID
    response = client.get("/api/links")
    assert response.status_code == 200, response.text

    link = next(
        item for item in response.json()
        if item["short_code"] == short_code
    )
    link_id = link["id"]

    # Delete it
    deleted = client.delete(f"/api/links/{link_id}")
    assert deleted.status_code == 204, deleted.text
    assert deleted.content == b""

    # Its details should no longer exist
    details = client.get(f"/api/links/{link_id}")
    assert details.status_code == 404, details.text

    # Deleting it again should return 404
    deleted_again = client.delete(f"/api/links/{link_id}")
    assert deleted_again.status_code == 404, deleted_again.text