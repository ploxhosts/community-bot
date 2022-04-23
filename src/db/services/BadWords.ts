import sequelize from "../database";
import { DataTypes, Model } from 'sequelize';

class BadWords extends Model {
    declare id: number;
    declare word: string;
    declare added_by: string;
    declare implicit: boolean;
}

BadWords.init({
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    word: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    added_by: {
        type: DataTypes.STRING,
        allowNull: false
    },
    implicit: {
        type: DataTypes.BOOLEAN,
        allowNull: false
    }

}, {
  sequelize,
  modelName: 'BadWords'
});
