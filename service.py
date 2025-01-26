from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    get_question_data = f"""
        DECLARE $question_id AS Uint64;

        SELECT question, options, correct_option
        FROM `quiz_questions`
        WHERE question_id == $question_id;
    """
    question_data = execute_select_query(pool, get_question_data, question_id=current_question_index)

    if len(question_data):
        if  question_data[0]["question"] and question_data[0]["options"] and question_data[0]["correct_option"]:
            return question_data[0]["question"], question_data[0]["options"], question_data[0]["correct_option"]
    # correct_index = quiz_data[current_question_index]['correct_option']
    # opts = quiz_data[current_question_index]['options']
    # kb = generate_options_keyboard(opts, opts[correct_index])
    # await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    await update_user(user_id)
    await get_question(user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]    


async def get_quiz_points(user_id):
    get_user_points = f"""
        DECLARE $user_id AS Uint64;

        SELECT user_points
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_points, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["user_points"] is None:
        return 0
    return results[0]["user_points"]    


async def update_quiz_index(user_id, question_index):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPDATE `quiz_state`
        SET `question_index` = $question_index
        WHERE user_id == $user_id;
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
    )


async def update_quiz_points(user_id, user_points):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $user_points AS Uint64;

        UPDATE `quiz_state`
        SET `user_points` = $user_points
        WHERE user_id == $user_id;
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        user_points=user_points,
    )


async def update_user(user_id):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;
        DECLARE $user_points AS Uint64;

        UPSERT INTO `quiz_state`(user_id, question_index, user_points)
        VALUES($user_id, $question_index, $user_points);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=0,
        user_points=0,
    )
