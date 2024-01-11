def example_function(name, age, gender='male', **kwargs):
    # 校验代码
    if not name:
        raise ValueError('name is required')

    if not age:
        raise ValueError('age is required')

    if gender not in ['male', 'female']:
        raise ValueError("gender must be either 'male' or 'female'")

    profile = kwargs.get("profile")
    if profile is None:
        raise ValueError('profile is required')

    address = profile.get("address")
    if not address:
        raise ValueError("address is required")

    # 业务代码
    print(name, age, gender, profile)


@ParamValidator("profile").is_similar_dict(reference_dict={"address": "", "school": ""})
@ParamValidator("gender", "gender must be either 'male' or 'female'").is_allowed("male", "female")
@ParamValidator("age", "age must be integer.").is_integer().is_not_empty()
@ParamValidator("name", "name must be string.").is_string().is_not_empty()
def example_function(name, age, gender='male', **kwargs):

    address = kwargs.get("profile").get("address")
    Validator(address).is_not_empty('address is required')

    # 业务代码
    print(name, age, gender, profile)
