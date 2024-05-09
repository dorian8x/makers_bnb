from playwright.sync_api import Page, expect

# Tests for your routes go here

"""
We can render the index page
"""
def test_get_home(page, test_web_address):
    # We load a virtual browser and navigate to the /home page
    page.goto(f"http://{test_web_address}/home")

    # We look at the <p> tag
    p_tag = page.locator("p").first

    # We assert that it has the text "This is the homepage."
    expect(p_tag).to_have_text("Book a beautiful space with MakersBNB for your ideal getaway! Look below for some inspiration:")


"""
Wee can render the sign up page
"""
def test_get_sign_up_page(page, test_web_address):
    # We load a virtual browser and navigate to the /index page
    page.goto(f"http://{test_web_address}/signup")
    # We look at the <h1> tag
    h1_tag = page.locator("h1")
    # We assert that it has the text "Register"
    expect(h1_tag).to_have_text("Register")
    
    # repeat for the form labels
    input_tag = page.get_by_label("Username:")
    expect(input_tag).to_have_id("username")

    input_tag = page.get_by_label("Password:")
    expect(input_tag).to_have_id("user_password")

    input_tag = page.get_by_label("Email:")
    expect(input_tag).to_have_id("email")

    input_tag = page.get_by_label("Full name:")
    expect(input_tag).to_have_id("full_name")


"""
Wee can render a single space page
"""
def test_get_test_page(page, test_web_address):
    page.goto(f"http://{test_web_address}/1")
    h1_tag  = page.locator('h1')
    expect(h1_tag).to_have_text("123 Main St")
    