from aiogram import Router, F
from aiogram.types import CallbackQuery
from tg_bot.lexicon import LEXICON_ANSWERS_RU
__all__ = ['router']

router = Router()


# @router.callback_query(F.data == 'book_page_back')
# async def process_book_page_back(callback: CallbackQuery):
#     await book_page_back(callback)
#
#
# @router.callback_query(F.data == 'book_page_next')
# async def process_book_page_back(callback: CallbackQuery):
#     await book_page_next(callback)
#
#
# @router.callback_query(F.data == 'book_page_now')
# async def process_add_bookmark(callback: CallbackQuery):
#     add_bookmark(callback)
#     await callback.answer(text=LEXICON_ANSWERS_RU['add_bookmark'])
#
#
# @router.callback_query(F.data.startswith('view_bookpage_'))
# async def process_go_to_page(callback: CallbackQuery):
#     page = int(callback.data.split('_')[-1])
#     keyboard = create_pages_kb(now_page=page, book=book)
#     await callback.message.edit_text(text=book[page], reply_markup=keyboard)
#
#
# @router.callback_query(F.data.startswith('del_bookpage_'))
# async def process_del_bookmark(callback: CallbackQuery):
#     await del_bookmark(callback)
#
#
# @router.callback_query(F.data == 'cancel_bookmark_pressed')
# async def process_cancel_bookmark(callback: CallbackQuery):
#     await callback.message.edit_text(text=LEXICON_ANSWERS_RU['continue_reading'])
#
#
# @router.callback_query(F.data == 'edit_bookmark_pressed')
# async def process_edit_bookmarks(callback: CallbackQuery):
#     keyboard = create_bookmarks_kb(callback, mode='edit')
# await
# callback.message.edit_text(text=LEXICON_ANSWERS_RU['edit_bookmarks'],
# reply_markup=keyboard)
