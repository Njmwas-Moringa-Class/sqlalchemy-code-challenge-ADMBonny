import os
import sys

sys.path.append(os.getcwd)

from sqlalchemy import (create_engine, PrimaryKeyConstraint, Column, String, ForeignKey, Integer)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship




Base = declarative_base()
engine = create_engine('sqlite:///db/restaurants.db', echo=True)


# class Review(Base):
#     pass

class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String())
    price = Column(Integer)
    reviews = relationship("Review", back_populates="restaurant")

    def __repr__(self):
        return f'Restaurant: {self.name}'

    def reviews(self):
        return session.query(Review).filter(Review.restaurant_id == self.id).all()

    def customers(self):
        return session.query(Customer).join(Review).filter(Review.restaurant_id == self.id).distinct().all()

    @classmethod
    def fanciest(cls):
        return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        return [f"Review for {self.name} by {review.customer.full_name()}: {review.star_rating} stars." for review in self.reviews]      

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String())
    last_name = Column(String())
    reviews = relationship("Review", back_populates="customer")

    def __repr__(self):
        return f'Customer: {self.name}'

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def reviews(self):
        return session.query(Review).filter(Review.customer_id == self.id).all()

    def restaurants(self):
        return session.query(Restaurant).join(Review).filter(Review.customer_id == self.id).distinct().all()

    def favorite_restaurant(self):
        return session.query(Restaurant, func.avg(Review.star_rating).label('average_rating')).join(Review).filter(Review.customer_id == self.id).group_by(Restaurant.id).order_by('average_rating DESC').first()

    def add_review(self, restaurant, rating):
        review = Review(customer_id=self.id, restaurant_id=restaurant.id, star_rating=rating)
        session.add(review)
        session.commit()

    def delete_reviews(self, restaurant):
        session.query(Review).filter(Review.customer_id == self.id, Review.restaurant_id == restaurant.id).delete()
        session.commit()

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant = relationship("Restaurant", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."
 
