from web_app import app
from web_app.models import Album, Portfolio
from flask import render_template

class PortfolioView():
    @app.route('/portfolios/<int:portfolio_id>')
    def get_portfolio(portfolio_id):
        portfolio = Portfolio.query.get(portfolio_id)
        primary_album = Album.query.get(portfolio.primary_album_id)
        return render_template('portfolio.html', portfolio=portfolio, primary_album=primary_album)

    @app.route('/portfolios')
    def get_all_portfolios():
        portfolios = Portfolio.query.all()
        return render_template('portfolios.html', portfolios=portfolios)

    @app.route('/portfolios/create')
    def create_portfolio():
        albums = Album.query.all()
        return render_template('create_portfolio.html', albums=albums)
