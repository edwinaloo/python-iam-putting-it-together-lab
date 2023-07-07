class Signup(Resource):
    def post(self):
        # Retrieve the user data from the request JSON
        username = request.json.get('username')
        password = request.json.get('password')
        # Validate the user data
        if not username or not password:
            return {'message': 'Username and password are required'}, 422
        try:
            # Create a new user and save it to the database
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            # Store the user's ID in the session
            session['user_id'] = user.id
            # Return the user's information in the response
            return {'user_id': user.id, 'username': user.username}, 201
        except IntegrityError:
            # Handle the case where the username is not unique
            db.session.rollback()
            return {'message': 'Username already exists'}, 422

class CheckSession(Resource):
    def get(self):
        # Check if the user is logged in
        if 'user_id' in session:
            # Retrieve the user based on the stored user ID
            user = User.query.get(session['user_id'])
            # Return the user's information in the response
            return {'user_id': user.id, 'username': user.username}, 200
        else:
            # Return an error message if the user is not logged in
            return {'message': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        # Retrieve the user data from the request JSON
        username = request.json.get('username')
        password = request.json.get('password')
        # Validate the user data
        if not username or not password:
            return {'message': 'Username and password are required'}, 422
        # Authenticate the user
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Store the user's ID in the session
            session['user_id'] = user.id
            # Return the user's information in the response
            return {'user_id': user.id, 'username': user.username}, 200
        else:
            # Return an error message if authentication fails
            return {'message': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        # Check if the user is logged in
        if 'user_id' in session:
            # Remove the user's ID from the session
            session.pop('user_id')
            # Return an empty response
            return {}, 204
        else:
            # Return an error message if the user is not logged in
            return {'message': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        # Check if the user is logged in
        if 'user_id' in session:
            # Retrieve all recipes associated with the logged-in user
            user = User.query.get(session['user_id'])
            recipes = user.recipes
            # Return the recipes and the associated user's information in the response
            return {'user_id': user.id, 'username': user.username, 'recipes': [recipe.serialize() for recipe in recipes]}, 200
        else:
            # Return an error message if the user is not logged in
            return {'message': 'Unauthorized'}, 401

    def post(self):
        # Check if the user is logged in
        if 'user_id' in session:
            # Retrieve the recipe data from the request JSON
            title = request.json.get('title')
            instructions = request.json.get('instructions')
            minutes_to_complete = request.json.get('minutes_to_complete')
            # Validate the recipe data
            if not title or not instructions:
                return {'message': 'Title and instructions are required'}, 422
            try:
                # Create a new recipe associated with the logged-in user
                user = User.query.get(session['user_id'])
                recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user=user)
                db.session.add(recipe)
                db.session.commit()
                # Return the recipe and the associated user's information in the response
                return {'user_id': user.id, 'username': user.username, 'recipe': recipe.serialize()}, 201
            except Exception as e:
                # Handle any errors that occur during recipe creation
                db.session.rollback()
                return {'message': 'Error creating recipe'}, 500
        else:
            # Return an error message if the user is not logged in
            return {'message': 'Unauthorized'}, 401
