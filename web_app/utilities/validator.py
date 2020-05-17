class Validator:
    def __init__(self, validations):
        self.validations = validations
        self.error_response = None

    def validate(self, request):
        for validation in self.validations:
            success, error_response = validation(request)
            if not success:
                self.error_response = error_response
                return False
        return True

    def get_error_response(self):
        return self.error_response
