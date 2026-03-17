"""
orangehrm パッケージ - OrangeHRM デモサイト用 Page Object Model

OrangeHRM デモサイト（https://opensource-demo.orangehrmlive.com/）を
操作するためのページオブジェクトクラス群。
"""
from pages.orangehrm.login_page import OrangeHRMLoginPage
from pages.orangehrm.dashboard_page import OrangeHRMDashboardPage
from pages.orangehrm.pim_page import OrangeHRMPimPage

__all__ = [
    "OrangeHRMLoginPage",
    "OrangeHRMDashboardPage",
    "OrangeHRMPimPage",
]
